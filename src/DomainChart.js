import React from 'react';
import ReactApexChart from 'react-apexcharts';

const RadialBarChart = ({ data }) => {
    const labels = data.map(item => item.category);
    const series = data.map(item => item.rating); // original, not squared

    const chartOptions = {
        chart: {
            type: 'radialBar',
        },
        plotOptions: {
            radialBar: {
                dataLabels: {
                    name: {
                        fontSize: '14px',
                    },
                    value: {
                        fontSize: '12px',
                    },
                },
                hollow: {
                    size: '30%',
                },
                track: {
                    show: true,
                    background: '#eee',
                    strokeWidth: '100%',
                },
                startAngle: 0,
                endAngle: 360,
                max: 10, // ✅ keep scale from 0–10
            },
        },
        labels: labels,
        colors: ['#ff6b6b', '#6bcBef', '#ffd93d', '#6fdd9c'],
    };

    return (
        <div style={{ width: 400, margin: 'auto' }}>
            <ReactApexChart
                options={chartOptions}
                series={series}
                type="radialBar"
                height={400}
            />
        </div>
    );
};

export default RadialBarChart;