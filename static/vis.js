// Line chart
$("#records").html("<p>" + records + "</p>");
$("#users").html("<p>" + users + "</p>");
$("#genres_count").html("<p>" + genres_count + "</p>");
var ctxL = document.getElementById("lineChart").getContext('2d');
var myLineChart = new Chart(ctxL,
	{
		type: 'line',
		data:
		{
			labels: ["7d", "6d", "5d", "4d", "3d", "2d", "Today"],
			datasets:
				[{
					data: counts,
					backgroundColor: ['rgba(139, 234, 236, .9)',],
					borderColor: ['#505250',],
					borderWidth: 2
				}]
		},
		options:
		{
			responsive: true,
			legend:
			{
				display: false
			}
		}
	});

// Pie chart
console.log(genres);
var ctxP = document.getElementById("pieChart").getContext('2d');
var myPieChart = new Chart(ctxP,
	{
		plugins: [ChartDataLabels],
		type: 'pie',
		data:
		{
			labels: ["Education", "Art", "Biology", "Computer Science", "Health", "Literature", "Politics", "Religion", "Sports"],
			datasets:
				[{
					data: genres,
					backgroundColor: ["#F7464A", "#46BFBD", "#FDB45C", "#71A06A", "#D9305A", "#8E6783", "#949FB1", "#4D5360", "#353231"],
					hoverBackgroundColor: ["#FF5A5E", "#5AD3D1", "#FFC870", "#A8B3C5", "#FF5A5E"]
				}]
		},
		options:
		{
			responsive: true,
			legend:
			{
				position: 'right',
				labels:
				{
					padding: 17,
					boxWidth: 10
				}
			},
			plugins:
			{
				datalabels:
				{
					formatter: (value, ctx) => {
						let sum = 0;
						let dataArr = ctx.chart.data.datasets[0].data;
						dataArr.map(data => {
							sum += data;
						});
						let percentage = (value * 100 / sum).toFixed(2) + "%";
						return percentage;
					},
					color: 'white',
					labels:
					{
						title:
						{
							font:
							{
								size: '10'
							}
						}
					}
				}
			}
		}
	});

// Bar chart horizontal
var ctxL = document.getElementById("barChartHorizontal").getContext('2d');
var myLineChart = new Chart(ctxL,
	{
		type: 'horizontalBar',
		data:
		{
			labels: words,
			datasets:
				[{
					data: w_count,
					backgroundColor: ["#F7464A", "#46BFBD", "#FDB45C", "#71A06A", "#8E6783"],
					borderWidth: 0,
				}]
		},
		options:
		{
			responsive: true,
			legend:
			{
				display: false,
			},
			tooltips:
			{
				intersect: false,
			},
			scales:
			{
				xAxes:
					[{
						stacked: true,
						gridLines:
						{
							display: true,
						},
						ticks:
						{
							fontColor: 'rgba(0,0,0, 0.5)',
						}
					}],
				yAxes:
					[{
						stacked: true,
						gridLines:
						{
							display: false,
							borderDash: [2],
							drawBorder: false,
							zeroLineColor: "rgba(0,0,0,0)",
							zeroLineBorderDash: [2],
							zeroLineBorderDashOffset: [2]
						},
						ticks:
						{
							fontColor: 'rgba(0,0,0, 0.5)'
						}
					}]
			}
		}
	});

//Bar Chart Vertical
var ctx = document.getElementById("myChart").getContext('2d');
var myChart = new Chart(ctx,
	{
		type: 'bar',
		data:
		{
			labels: titles,
			datasets:
				[{
					label: 'Page rank',
					data: ranks,
					backgroundColor:
						["#F7464A", "#46BFBD", "#FDB45C", "#71A06A", "#8E6783"],
					borderColor:
						[
							'rgba(255,99,132,1)',
							'rgba(54, 162, 235, 1)',
							'rgba(255, 206, 86, 1)',
							'rgba(75, 192, 192, 1)',
							'rgba(153, 102, 255, 1)',
							'rgba(255, 159, 64, 1)'
						],
					borderWidth: 1
				}]
		},
		options:
		{
			scales:
			{
				yAxes:
					[{
						ticks:
						{
							beginAtZero: true
						}
					}]
			},
			legend:
			{
				display: false
			}
		}
	});