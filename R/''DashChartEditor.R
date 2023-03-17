# AUTO GENERATED FILE - DO NOT EDIT

#' @export
''DashChartEditor <- function(id=NULL, annotateOptions=NULL, config=NULL, controlOptions=NULL, data=NULL, dataSources=NULL, frames=NULL, layout=NULL, loadFigure=NULL, logoSrc=NULL, logoStyle=NULL, structureOptions=NULL, style=NULL, styleOptions=NULL, traceOptions=NULL) {
    
    props <- list(id=id, annotateOptions=annotateOptions, config=config, controlOptions=controlOptions, data=data, dataSources=dataSources, frames=frames, layout=layout, loadFigure=loadFigure, logoSrc=logoSrc, logoStyle=logoStyle, structureOptions=structureOptions, style=style, styleOptions=styleOptions, traceOptions=traceOptions)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashChartEditor',
        namespace = 'dash_chart_editor',
        propNames = c('id', 'annotateOptions', 'config', 'controlOptions', 'data', 'dataSources', 'frames', 'layout', 'loadFigure', 'logoSrc', 'logoStyle', 'structureOptions', 'style', 'styleOptions', 'traceOptions'),
        package = 'dashChartEditor'
        )

    structure(component, class = c('dash_component', 'list'))
}
