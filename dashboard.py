import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv"
)

data = pd.read_csv(DATA_URL)

app = dash.Dash(__name__)
app.title = "Automobile Sales Analytics"
server = app.server

REPORT_OPTIONS = [
    {"label": "Yearly Statistics", "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]

YEAR_OPTIONS = [
    {"label": year, "value": year}
    for year in sorted(data["Year"].dropna().astype(int).unique())
]


def style_figure(fig):
    fig.update_layout(
        template="plotly_white",
        font={"family": "Arial, sans-serif", "size": 13, "color": "#172B4D"},
        title={"font": {"size": 18}, "x": 0.03, "xanchor": "left"},
        margin={"l": 55, "r": 25, "t": 70, "b": 50},
        height=390,
        legend_title_text="",
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False, linecolor="#DFE3E8")
    fig.update_yaxes(gridcolor="#EEF1F4", zeroline=False)
    return fig


def graph_card(fig):
    return html.Div(
        dcc.Graph(
            figure=style_figure(fig),
            config={"displayModeBar": False, "responsive": True},
            style={"height": "100%"},
        ),
        className="chart-card",
    )


app.layout = html.Div(
    [
        html.Div(
            [
                html.Div("PORTFOLIO PROJECT", className="eyebrow"),
                html.H1("Automobile Sales Analytics"),
                html.P(
                    "Interactive analysis of sales performance across yearly and recession conditions.",
                    className="subtitle",
                ),
            ],
            className="hero",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Report type"),
                        dcc.Dropdown(
                            id="dropdown-statistics",
                            options=REPORT_OPTIONS,
                            value=None,
                            placeholder="Select a report type",
                            clearable=False,
                        ),
                    ],
                    className="control",
                ),
                html.Div(
                    [
                        html.Label("Year"),
                        dcc.Dropdown(
                            id="select-year",
                            options=YEAR_OPTIONS,
                            value=None,
                            placeholder="Select a year",
                            clearable=False,
                            disabled=True,
                        ),
                    ],
                    className="control year-control",
                ),
            ],
            className="control-panel",
        ),
        html.Div(
            "Choose a report type above to explore the dashboard.",
            id="output-container",
            className="dashboard-grid empty-state",
        ),
        html.Div(
            "Source: IBM Skills Network automobile sales dataset",
            className="footer",
        ),
    ],
    className="page-shell",
)


@app.callback(
    Output("select-year", "disabled"),
    Input("dropdown-statistics", "value"),
)
def update_year_dropdown(selected_statistics):
    return selected_statistics != "Yearly Statistics"


@app.callback(
    Output("output-container", "children"),
    Output("output-container", "className"),
    Input("dropdown-statistics", "value"),
    Input("select-year", "value"),
)
def update_dashboard(selected_statistics, selected_year):
    if selected_statistics == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1]

        yearly_rec = (
            recession_data.groupby("Year", as_index=False)["Automobile_Sales"].mean()
        )
        fig1 = px.line(
            yearly_rec,
            x="Year",
            y="Automobile_Sales",
            markers=True,
            title="Average Sales During Recessions",
            labels={"Automobile_Sales": "Average automobile sales"},
        )

        average_sales = (
            recession_data.groupby("Vehicle_Type", as_index=False)["Automobile_Sales"].mean()
        )
        fig2 = px.bar(
            average_sales,
            x="Vehicle_Type",
            y="Automobile_Sales",
            title="Average Sales by Vehicle Type",
            labels={"Vehicle_Type": "Vehicle type", "Automobile_Sales": "Average sales"},
        )

        ad_spend = (
            recession_data.groupby("Vehicle_Type", as_index=False)["Advertising_Expenditure"].sum()
        )
        fig3 = px.pie(
            ad_spend,
            values="Advertising_Expenditure",
            names="Vehicle_Type",
            hole=0.45,
            title="Advertising Spend by Vehicle Type",
        )

        unemp_data = (
            recession_data.groupby(
                ["unemployment_rate", "Vehicle_Type"], as_index=False
            )["Automobile_Sales"].mean()
        )
        fig4 = px.bar(
            unemp_data,
            x="unemployment_rate",
            y="Automobile_Sales",
            color="Vehicle_Type",
            barmode="group",
            title="Sales vs. Unemployment Rate",
            labels={
                "unemployment_rate": "Unemployment rate",
                "Automobile_Sales": "Average automobile sales",
                "Vehicle_Type": "Vehicle type",
            },
        )

        return [
            graph_card(fig1),
            graph_card(fig2),
            graph_card(fig3),
            graph_card(fig4),
        ], "dashboard-grid"

    if selected_statistics == "Yearly Statistics":
        if selected_year is None:
            return "Select a year to display the yearly dashboard.", "dashboard-grid empty-state"

        yearly_data = data[data["Year"] == selected_year]

        annual_sales = data.groupby("Year", as_index=False)["Automobile_Sales"].mean()
        fig1 = px.line(
            annual_sales,
            x="Year",
            y="Automobile_Sales",
            markers=True,
            title="Annual Automobile Sales",
            labels={"Automobile_Sales": "Average automobile sales"},
        )
        fig1.add_vline(x=selected_year, line_dash="dash", opacity=0.45)

        monthly_sales = (
            yearly_data.groupby("Month", as_index=False)["Automobile_Sales"].sum()
        )
        fig2 = px.line(
            monthly_sales,
            x="Month",
            y="Automobile_Sales",
            markers=True,
            title=f"Monthly Sales — {selected_year}",
            labels={"Month": "Month", "Automobile_Sales": "Total automobile sales"},
        )

        vehicle_sales = (
            yearly_data.groupby("Vehicle_Type", as_index=False)["Automobile_Sales"].mean()
        )
        fig3 = px.bar(
            vehicle_sales,
            x="Vehicle_Type",
            y="Automobile_Sales",
            title=f"Average Sales by Vehicle Type — {selected_year}",
            labels={"Vehicle_Type": "Vehicle type", "Automobile_Sales": "Average sales"},
        )

        yearly_ad_spend = (
            yearly_data.groupby("Vehicle_Type", as_index=False)["Advertising_Expenditure"].sum()
        )
        fig4 = px.pie(
            yearly_ad_spend,
            values="Advertising_Expenditure",
            names="Vehicle_Type",
            hole=0.45,
            title=f"Advertising Spend by Vehicle Type — {selected_year}",
        )

        return [
            graph_card(fig1),
            graph_card(fig2),
            graph_card(fig3),
            graph_card(fig4),
        ], "dashboard-grid"

    return "Choose a report type above to explore the dashboard.", "dashboard-grid empty-state"


if __name__ == "__main__":
    app.run(debug=True)
