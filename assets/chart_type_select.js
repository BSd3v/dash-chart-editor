/**
 * Custom renderOption function for the chart-type Select in PydanticChartEditor.
 *
 * Each option is expected to carry:
 *   option.value       – px function name, e.g. "scatter"
 *   option.label       – human-readable label, e.g. "Scatter"
 *   option.description – one-liner description, e.g. "X vs Y scatter plot"
 *
 * Referenced in Python via: renderOption={"function": "chartTypeRenderOption"}
 */
window.chartTypeRenderOption = function ({ option }) {
    const label = option.label || option.value || "";
    const description = option.description || "";

    return React.createElement(
        "div",
        {
            style: {
                display: "flex",
                flexDirection: "column",
                gap: "4px",
                padding: "2px 0",
            },
        },
        React.createElement(
            "span",
            { style: { fontWeight: 500, lineHeight: "1.3" } },
            label
        ),
        description
            ? React.createElement(
                  "span",
                  {
                      style: {
                          fontSize: "11px",
                          color: "var(--mantine-color-dimmed, #868e96)",
                          lineHeight: "1.2",
                      },
                  },
                  description
              )
            : null
    );
};
