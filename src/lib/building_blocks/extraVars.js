export const SPLIT_ALLOWED = ['scattermapbox', 'scattergeo']

export const traceTypes = (_, chartCategory, traceOptions) => {

    var traces = [
      {
        value: 'scatter',
        label: _('Scatter'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'bar',
        label: _('Bar'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'line',
        label: _('Line'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'area',
        label: _('Area'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'heatmap',
        label: _('Heatmap'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'table',
        label: _('Table'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'contour',
        label: _('Contour'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'pie',
        label: _('Pie'),
        category: chartCategory(_).SIMPLE,
      },
      {
        value: 'scatter3d',
        label: _('3D Scatter'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'line3d',
        label: _('3D Line'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'surface',
        label: _('3D Surface'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'mesh3d',
        label: _('3D Mesh'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'cone',
        label: _('Cone'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'streamtube',
        label: _('Streamtube'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'box',
        label: _('Box'),
        category: chartCategory(_).DISTRIBUTIONS,
      },
      {
        value: 'violin',
        label: _('Violin'),
        category: chartCategory(_).DISTRIBUTIONS,
      },
      {
        value: 'histogram',
        label: _('Histogram'),
        category: chartCategory(_).DISTRIBUTIONS,
      },
      {
        value: 'histogram2d',
        label: _('2D Histogram'),
        category: chartCategory(_).DISTRIBUTIONS,
      },
      {
        value: 'histogram2dcontour',
        label: _('2D Contour Histogram'),
        category: chartCategory(_).DISTRIBUTIONS,
      },
      {
        value: 'scattermapbox',
        label: _('Tile Map'),
        category: chartCategory(_).MAPS,
      },
      {
        value: 'scattergeo',
        label: _('Atlas Map'),
        category: chartCategory(_).MAPS,
      },
      {
        value: 'choroplethmapbox',
        label: _('Choropleth Tile Map'),
        category: chartCategory(_).MAPS,
      },
      {
        value: 'choropleth',
        label: _('Choropleth Atlas Map'),
        category: chartCategory(_).MAPS,
      },
      {
        value: 'densitymapbox',
        label: _('Density Tile Map'),
        category: chartCategory(_).MAPS,
      },
      {
        value: 'scatterpolar',
        label: _('Polar Scatter'),
        category: chartCategory(_).SPECIALIZED,
      },
      {
        value: 'barpolar',
        label: _('Polar Bar'),
        category: chartCategory(_).SPECIALIZED,
      },
      {
        value: 'scatterternary',
        label: _('Ternary Scatter'),
        category: chartCategory(_).SPECIALIZED,
      },
      {
        value: 'sunburst',
        label: _('Sunburst'),
        category: chartCategory(_).SPECIALIZED,
      },
      {
        value: 'treemap',
        label: _('Treemap'),
        category: chartCategory(_).SPECIALIZED,
      },
      {
        value: 'sankey',
        label: _('Sankey'),
        category: chartCategory(_).SPECIALIZED,
      },
      {
        value: 'candlestick',
        label: _('Candlestick'),
        category: chartCategory(_).FINANCIAL,
      },
      {
        value: 'ohlc',
        label: _('OHLC'),
        category: chartCategory(_).FINANCIAL,
      },
      {
        value: 'waterfall',
        label: _('Waterfall'),
        category: chartCategory(_).FINANCIAL,
      },
      {
        value: 'funnel',
        label: _('Funnel'),
        category: chartCategory(_).FINANCIAL,
      },
      {
        value: 'funnelarea',
        label: _('Funnel Area'),
        category: chartCategory(_).FINANCIAL,
      },
      {
        value: 'scattergl',
        icon: 'scatter',
        label: _('Scatter'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'scatterpolargl',
        icon: 'scatterpolar',
        label: _('Polar Scatter'),
        category: chartCategory(_).THREE_D,
      },
      {
        value: 'heatmapgl',
        icon: 'heatmap',
        label: _('Heatmap GL'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'pointcloud',
        label: _('Point Cloud'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'parcoords',
        label: _('Parallel Coordinates'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'parcats',
        label: _('Parallel Categories'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'splom',
        label: _('Scatterplot Matrix'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'scattercarpet',
        label: _('Scatter Carpet'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'contourcarpet',
        label: _('Contour Carpet'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'carpet',
        label: _('Carpet'),
        category: chartCategory(_).HIDDEN,
      },
      {
        value: 'isosurface',
        label: _('Isosurface'),
        category: chartCategory(_).HIDDEN,
      },
    ]

    if (traceOptions) {
        return traces.filter((v) => traceOptions.includes(v.value))
    } else {
        return traces
    }

}

export const categoryLayout = (_, chartCategory, traces) => {
    var categories = [
      chartCategory(_).SIMPLE,
      chartCategory(_).DISTRIBUTIONS,
      chartCategory(_).THREE_D,
      chartCategory(_).MAPS,
      chartCategory(_).FINANCIAL,
      chartCategory(_).SPECIALIZED,
    ];

    var catsMapped = []
    traces(_).map((t) => {if (!catsMapped.includes(t.category.value)) {catsMapped.push(t.category.value)}})

    var newCats = []
    categories.map((v) => {if (catsMapped.includes(v.value)) {newCats.push(v)}})

    return newCats
}