
colors_dashed = ['#004466', '#0088CC', '#33BBFF', '#99DDFF', '#00FFFF'];
colors_normal = ['#660011', '#CC0022', '#FF3355', '#FF99AA', '#FF0080'];

function generateChartData(chart) {
    let color_index_normal = 0;
    let color_index_dashed = 0;

    const data = {
        series: chart.series.map(s => (({ name, data }) => ({ name, data }))(s)),
        chart: {
            height: 350,
            type: 'line',
            dropShadow: {
                enabled: true,
                color: '#000',
                top: 18,
                left: 7,
                blur: 10,
                opacity: 0.2
            },
            toolbar: {
                show: false
            }
        },
        colors: chart.series.map(s => {
            let color;
            if (s.dashed) {
                color = colors_dashed[color_index_dashed]
                color_index_dashed = color_index_dashed + 1 % colors_dashed.length
            } else {
                color = colors_normal[color_index_normal]
                color_index_normal = color_index_normal + 1 % colors_normal.length
            }

            return color
        }),
        dataLabels: {
            enabled: false,
        },
        stroke: {
            curve: 'smooth',
            dashArray: chart.series.map(s => (s.dashed ? 5 : 0)),
        },
        title: {
            text: chart.title,
            align: 'left'
        },
        grid: {
            borderColor: '#e7e7e7',
            row: {
                colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
                opacity: 0.5
            },
        },
        markers: {
            size: 1
        },
        xaxis: {
            type: "numeric",
            title: {
                text: chart.axes.x.name
            }
        },
        yaxis: {
            type: "numeric",
            title: {
                text: chart.axes.y.name
            },
        },
        legend: {
            position: 'top',
            horizontalAlign: 'right',
            floating: true,
            offsetY: -25,
            offsetX: -5
        },
        tooltip: {
            x: {
                formatter: function (value) {
                    return `${value} ${chart.axes.x.unit}`;
                }
            },
            y: {
                formatter: function (value) {
                    return `${value} ${chart.axes.y.unit}`;
                }
            }
        }
    };
    return data;
}

const charts = {};

function loadCharts() {
    let file = "data.json"

    const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
    });

    console.log(params);

    if (params.file) {
        file = params.file;
    }

    fetch(file).then((rsp) => {
        rsp.json().then((chartsRaw) => {
            chartsRaw.forEach((chart) => {
                const chartData = generateChartData(chart);

                console.log(chartData);

                document.querySelector(`#charts`).insertAdjacentHTML("beforeend",`
                <div id="${chart.id}"></div>
                <br/><br/><br/>
                `);

                charts[chart.id] = new ApexCharts(document.querySelector(`#${chart.id}`), chartData);
                charts[chart.id].render();
            });
        });
    });
}



document.addEventListener("DOMContentLoaded", function () {
    loadCharts();
});

