# AUTO GENERATED FILE - DO NOT EDIT

#' @export
''DashChartEditor <- function(id=NULL, annotateOptions=NULL, config=NULL, controlOptions=NULL, dataSources=NULL, figure=NULL, loadFigure=NULL, logoSrc=NULL, logoStyle=NULL, saveState=NULL, structureOptions=NULL, style=NULL, styleOptions=NULL, traceOptions=NULL) {
    
    props <- list(id=id, annotateOptions=annotateOptions, config=config, controlOptions=controlOptions, dataSources=dataSources, figure=figure, loadFigure=loadFigure, logoSrc=logoSrc, logoStyle=logoStyle, saveState=saveState, structureOptions=structureOptions, style=style, styleOptions=styleOptions, traceOptions=traceOptions)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashChartEditor',
        namespace = 'dash_chart_editor',
        propNames = c('id', 'annotateOptions', 'config', 'controlOptions', 'dataSources', 'figure', 'loadFigure', 'logoSrc', 'logoStyle', 'saveState', 'structureOptions', 'style', 'styleOptions', 'traceOptions'),
        package = 'dashChartEditor'
        )

    structure(component, class = c('dash_component', 'list'))
}
