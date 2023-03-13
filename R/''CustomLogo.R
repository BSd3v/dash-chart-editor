# AUTO GENERATED FILE - DO NOT EDIT

#' @export
''CustomLogo <- function(src=NULL, style=NULL) {
    
    props <- list(src=src, style=style)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'CustomLogo',
        namespace = 'dash_chart_editor',
        propNames = c('src', 'style'),
        package = 'dashChartEditor'
        )

    structure(component, class = c('dash_component', 'list'))
}
