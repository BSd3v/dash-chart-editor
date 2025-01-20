export const SPLIT_ALLOWED = ['scattermapbox', 'scattergeo'];

function toProperCase(str) {
    return str.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

export const currentSchema = () => {
    return window.Plotly.PlotSchema.get();
};

export const chartCategory = (_) => {
    return {
        SIMPLE: {
            value: 'SIMPLE',
            label: _('Simple'),
        },
        FINANCIAL: {
            value: 'FINANCIAL',
            label: _('Finance'),
            maxColumns: 1,
        },
        DISTRIBUTIONS: {
            value: 'DISTRIBUTIONS',
            label: _('Distributions'),
        },
        MAPS: {
            value: 'MAPS',
            label: _('Maps'),
            maxColumns: 1,
        },
        SPECIALIZED: {
            value: 'SPECIALIZED',
            label: _('Specialized'),
            maxColumns: 1,
        },
        THREE_D: {
            value: '3D',
            label: _('3D'),
            maxColumns: 1,
        },
        HIDDEN: {
            value: 'HIDDEN',
            label: 'Hidden',
        },
        OTHER: {
            value: 'OTHER',
            label: _('Other'),
        },
    };
};

export const traceTypes = (_, traceOptions) => {
    var dce_vars = (window.DCE_vars = window.DCE_vars || {});
    var allTraces;
    if (dce_vars.allTraces) {
        allTraces = dce_vars.allTraces;
    } else {
        allTraces = Object.keys(currentSchema().traces);
        dce_vars.allTraces = allTraces;
    }

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
            value: 'indicator',
            label: _('Indicator'),
            category: chartCategory(_).SIMPLE,
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
            category: chartCategory(_).HIDDEN,
        },
    ];

    traces.map((v) => {
        if (allTraces.includes(v.value)) {
            allTraces.splice(allTraces.indexOf(v.value), 1);
        }
    });

    allTraces.map((v) =>
        traces.push({
            value: v,
            label: _(toProperCase(v)),
            category: chartCategory(_).OTHER,
        })
    );

    if (traceOptions) {
        return traces.filter((v) => traceOptions.includes(v.value));
    }
    return traces;
};

export const categoryLayout = (_, traces) => {
    var catsMapped = [];
    var categories = [];
    traces(_).map((t) => {
        if (
            !catsMapped.includes(t.category.value) &&
            t.category.value !== 'HIDDEN'
        ) {
            catsMapped.push(t.category.value);
            categories.push(t.category);
        }
    });

    return categories;
};

export const computeTraceOptionsFromSchema = (schema, _, context) => {
    // Filter out Polar "area" type as it is fairly broken and we want to present
    // scatter with fill as an "area" chart type for convenience.
    const traceTypes = Object.keys(schema.traces).filter(
        (t) => !['area', 'scattermapbox'].includes(t)
    );

    var traces = [
        {
            value: 'scatter',
            label: _('Scatter'),
        },
        {
            value: 'bar',
            label: _('Bar'),
        },
        {
            value: 'line',
            label: _('Line'),
        },
        {
            value: 'area',
            label: _('Area'),
        },
        {
            value: 'heatmap',
            label: _('Heatmap'),
        },
        {
            value: 'table',
            label: _('Table'),
        },
        {
            value: 'contour',
            label: _('Contour'),
        },
        {
            value: 'pie',
            label: _('Pie'),
        },
        {
            value: 'scatter3d',
            label: _('3D Scatter'),
        },
        {
            value: 'line3d',
            label: _('3D Line'),
        },
        {
            value: 'surface',
            label: _('3D Surface'),
        },
        {
            value: 'mesh3d',
            label: _('3D Mesh'),
        },
        {
            value: 'cone',
            label: _('Cone'),
        },
        {
            value: 'streamtube',
            label: _('Streamtube'),
        },
        {
            value: 'box',
            label: _('Box'),
        },
        {
            value: 'violin',
            label: _('Violin'),
        },
        {
            value: 'histogram',
            label: _('Histogram'),
        },
        {
            value: 'histogram2d',
            label: _('2D Histogram'),
        },
        {
            value: 'histogram2dcontour',
            label: _('2D Contour Histogram'),
        },
        {
            value: 'scattermapbox',
            label: _('Tile Map'),
        },
        {
            value: 'scattergeo',
            label: _('Atlas Map'),
        },
        {
            value: 'choroplethmapbox',
            label: _('Choropleth Tile Map'),
        },
        {
            value: 'choropleth',
            label: _('Choropleth Atlas Map'),
        },
        {
            value: 'densitymapbox',
            label: _('Density Tile Map'),
        },
        {
            value: 'scatterpolar',
            label: _('Polar Scatter'),
        },
        {
            value: 'barpolar',
            label: _('Polar Bar'),
        },
        {
            value: 'scatterternary',
            label: _('Ternary Scatter'),
        },
        {
            value: 'sunburst',
            label: _('Sunburst'),
        },
        {
            value: 'treemap',
            label: _('Treemap'),
        },
        {
            value: 'sankey',
            label: _('Sankey'),
        },
        {
            value: 'candlestick',
            label: _('Candlestick'),
        },
        {
            value: 'ohlc',
            label: _('OHLC'),
        },
        {
            value: 'waterfall',
            label: _('Waterfall'),
        },
        {
            value: 'funnel',
            label: _('Funnel'),
        },
        {
            value: 'funnelarea',
            label: _('Funnel Area'),
        },
        {
            value: 'scattergl',
            icon: 'scatter',
            label: _('Scatter'),
        },
        {
            value: 'scatterpolargl',
            icon: 'scatterpolar',
            label: _('Polar Scatter'),
        },
        {
            value: 'heatmapgl',
            icon: 'heatmap',
            label: _('Heatmap GL'),
        },
        {
            value: 'pointcloud',
            label: _('Point Cloud'),
        },
        {
            value: 'parcoords',
            label: _('Parallel Coordinates'),
        },
        {
            value: 'parcats',
            label: _('Parallel Categories'),
        },
        {
            value: 'splom',
            label: _('Scatterplot Matrix'),
        },
        {
            value: 'scattercarpet',
            label: _('Scatter Carpet'),
        },
        {
            value: 'contourcarpet',
            label: _('Contour Carpet'),
        },
        {
            value: 'carpet',
            label: _('Carpet'),
        },
        {
            value: 'isosurface',
            label: _('Isosurface'),
        },
        {
            value: 'indicator',
            label: _('Indicator'),
        },
    ];

    const traceOptions = traces.filter(
        (obj) => traceTypes.indexOf(obj.value) !== -1
    );

    const traceIndex = (traceType) =>
        traceOptions.findIndex((opt) => opt.value === traceType);

    traceOptions.splice(
        traceIndex('scatter') + 1,
        0,
        {label: _('Line'), value: 'line'},
        {label: _('Area'), value: 'area'},
        {label: _('Timeseries'), value: 'timeseries'}
    );

    traceOptions.splice(traceIndex('scatter3d') + 1, 0, {
        label: _('3D Line'),
        value: 'line3d',
    });

    if (context.config && context.config.mapboxAccessToken) {
        traceOptions.push({
            value: 'scattermapbox',
            label: _('Satellite Map'),
        });
    }

    return traceOptions;
};

export const nestedTest = (props) => {
    var style = {};
    if (props.test && !props.bypass) {
        style = {display: 'none'};

        try {
            if (props.parent) {
                if (props.container[props.parent].includes(props.test)) {
                    style = {};
                }
            } else {
                if (Object.keys(props.container).includes(props.test)) {
                    style = {};
                }
            }
        } catch {
            style = {display: 'none'};
        }
    }
    return style;
};
