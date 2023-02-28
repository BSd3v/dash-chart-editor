# AUTO GENERATED FILE - DO NOT EDIT

#' @export
''DashChartEditor <- function(children=NULL, id=NULL, data=NULL, dataSources=NULL, frames=NULL, layout=NULL, loadFigure=NULL, style=NULL) {
    
    props <- list(children=children, id=id, data=data, dataSources=dataSources, frames=frames, layout=layout, loadFigure=loadFigure, style=style)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DashChartEditor',
        namespace = 'dash_chart_editor',
        propNames = c('children', 'id', 'data', 'dataSources', 'frames', 'layout', 'loadFigure', 'style'),
        package = 'dashChartEditor'
        )

    structure(component, class = c('dash_component', 'list'))
}
