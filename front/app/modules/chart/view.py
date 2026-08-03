from __future__ import annotations

import math

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QLabel, QStackedLayout, QVBoxLayout, QWidget

from app.shared.theme import Color, page_subtitle, page_title


class ChartView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = page_title("Flight Charts")
        self._subtitle = page_subtitle("Summary of your latest search results")

        self._stack = QStackedLayout()

        self._empty_label = QLabel("Run a search first to see charts.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {Color.SLATE_500}; font-size: 16px;")

        self._charts_container = QWidget()
        charts_layout = QVBoxLayout(self._charts_container)
        charts_layout.setSpacing(20)

        self._count_chart_view = QChartView()
        self._secondary_chart_view = QChartView()
        for chart_view in (self._count_chart_view, self._secondary_chart_view):
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            chart_view.setMinimumHeight(220)
            chart_view.setMaximumHeight(300)
            charts_layout.addWidget(chart_view)

        charts_layout.addStretch()

        empty_page = QWidget()
        empty_layout = QVBoxLayout(empty_page)
        empty_layout.addStretch()
        empty_layout.addWidget(self._empty_label)
        empty_layout.addStretch()

        self._stack.addWidget(empty_page)
        self._stack.addWidget(self._charts_container)

        layout.addWidget(title)
        layout.addWidget(self._subtitle)
        layout.addLayout(self._stack, stretch=1)

    def show_empty(self) -> None:
        self._stack.setCurrentIndex(0)

    def show_charts(
        self,
        count_by_airline: dict[str, int],
        secondary_title: str,
        secondary_data: dict[str, float],
        secondary_is_delay: bool,
    ) -> None:
        if secondary_is_delay:
            self._subtitle.setText("Airline counts and average departure delays")
        else:
            self._subtitle.setText(
                "Airline counts and flight status — "
                "no delay data was reported for these flights"
            )

        self._count_chart_view.setChart(
            self._build_bar_chart(
                title="Flights by Airline",
                data={k: float(v) for k, v in count_by_airline.items()},
                color="#2563eb",
                integer_axis=True,
            )
        )
        self._secondary_chart_view.setChart(
            self._build_bar_chart(
                title=secondary_title,
                data=secondary_data,
                color="#0891b2" if secondary_is_delay else "#0d9488",
                integer_axis=not secondary_is_delay,
            )
        )
        self._stack.setCurrentIndex(1)

    def _build_bar_chart(
        self,
        title: str,
        data: dict[str, float],
        color: str,
        integer_axis: bool,
    ) -> QChart:
        if not data:
            chart = QChart()
            chart.setTitle(f"{title}\n(no data)")
            return chart

        categories = list(data.keys())
        values = [float(data[cat]) for cat in categories]

        bar_set = QBarSet("")
        bar_set.setColor(color)
        for value in values:
            bar_set.append(value)

        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().hide()
        chart.setMargins(QMargins(4, 4, 4, 4))

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_val = max(values)
        if integer_axis:
            y_max = max(1, int(math.ceil(max_val)))
            axis_y.setRange(0, y_max)
            axis_y.setTickInterval(1)
            axis_y.setTickCount(y_max + 1)
            axis_y.setLabelFormat("%d")
        else:
            y_max = max(1.0, math.ceil(max_val))
            axis_y.setRange(0, y_max)
            axis_y.setTickCount(min(6, int(y_max) + 1))
            axis_y.setLabelFormat("%.0f")

        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        return chart
