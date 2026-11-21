from pathlib import Path

import streamlit.components.v1 as components


_GLOBE_COMPONENT = components.declare_component(
    "overview_interactive_globe",
    path=str(Path(__file__).resolve().parent / "components" / "overview_globe"),
)


def render_globe_component(
    figure_json,
    height,
    key,
    selected_regions=None,
    selection_mode="single",
):
    return _GLOBE_COMPONENT(
        figure_json=figure_json,
        height=height,
        key=key,
        selected_regions=selected_regions or [],
        selection_mode=selection_mode,
    )
