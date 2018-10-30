// colors from color brewer
var blues = ['rgb(247,251,255)', 'rgb(222,235,247)', 'rgb(198,219,239)',
              'rgb(158,202,225)', 'rgb(107,174,214)', 'rgb(66,146,198)',
              'rgb(33,113,181)', 'rgb(8,69,148)']
var purps = ['rgb(252,251,253)', 'rgb(239,237,245)', 'rgb(218,218,235)',
              'rgb(188,189,220)', 'rgb(158,154,200)', 'rgb(128,125,186)',
              'rgb(106,81,163)', 'rgb(84,39,143)', 'rgb(63,0,125)']
var warm = ['rgb(255,247,236)', 'rgb(254,232,200)', 'rgb(253,212,158)',
            'rgb(253,187,132)', 'rgb(252,141,89)', 'rgb(239,101,72)',
            'rgb(215,48,31)', 'rgb(153,0,0)']
var warm2 = ['rgb(255,255,204)', 'rgb(255,237,160)', 'rgb(254,217,118)',
             'rgb(254,178,76)', 'rgb(253,141,60)', 'rgb(252,78,42)',
             'rgb(227,26,28)', 'rgb(177,0,38)']
var purp2 = ['rgb(255,247,243)', 'rgb(253,224,221)', 'rgb(252,197,192)',
             'rgb(250,159,181)', 'rgb(247,104,161)', 'rgb(221,52,151)',
             'rgb(174,1,126)', 'rgb(122,1,119)']

function plot_data(all_data, colormap) {
  var ctx = document.getElementById("chartCanvas");
  var chart = new Chart(ctx, {
    type: 'line',
    // data information
    data: {
        labels: ["1 Month", "3 Months", "6 Months", "1 Year",
                 "2 Years", "3 Years", "5 Years", "7 Years",
                 "10 Years", "20 Years", "30 Years"],
        datasets: []
    },

    // chart configuration
    options: {
      title: {
        display: true,
        text: 'U.S. Treasury Bond Yield vs. Maturity',
        fontSize: 30
      },
      scales: {
        yAxes: [{
          display: true,
          scaleLabel: {
            display: true,
            labelString: 'Annual Yield [%]',
            fontSize: 24
          },
          ticks: {
            fontSize: 16
          }
        }],
        xAxes: [{
          display: true,
          scaleLabel: {
            display: true,
            labelString: 'Maturity',
            fontSize: 24
          },
          ticks: {
            fontSize: 16
          }
        }]
      },
      legend: {
        position: 'right',
        labels: {
            fontSize: 16
        }
      }
    }
  });

  // add a dataset for each pushed
  for (var i = 0; i < all_data.length; i++)
  {
    var data = all_data[i];
    var newDataset = {
      label: data.label,
      borderColor: colormap[colormap.length - (i % colormap.length) - 1],
      backgroundColor: colormap[colormap.length - (i % colormap.length) - 1],
      data: data.data,
      spanGaps: true,
      fill: false
    };

    chart.data.datasets.push(newDataset);
  }

  chart.update();
}

function enable_picker(colormap) {
  var today = new Date();
  var picker = new Pikaday(
  {
      field: document.getElementById('datepicker'),
      format: 'YYYY-MM-DD',
      firstDay: 1,
      minDate: new Date(1990, 0, 1),
      maxDate: today,
      yearRange: [1989, today.getFullYear() + 1],
      disableWeekends: true
  });

  document.getElementById('addDataset').addEventListener('click', function() {
    var n = chart.data.datasets.length;
    getJSON("yields/" + picker.toString(),
      function(err, data) {
        var newDataset = {
          label: picker.toString(),
          borderColor: colormap[colormap.length - (n % colormap.length) - 1],
          backgroundColor: colormap[colormap.length - (n % colormap.length) - 1],
          data: data.data,
          fill: false
        };

        chart.data.datasets.push(newDataset);
        window.chart.update();
      });
  });

  document.getElementById('newChart').addEventListener('click', function() {
    location.href = picker.toString();
  });
}

var getJSON = function(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'json';
  xhr.onload = function() {
    var status = xhr.status;
    if (status === 200) {
      callback(null, xhr.response);
    } else {
      callback(status, xhr.response);
    }
  };

  xhr.send();
};
