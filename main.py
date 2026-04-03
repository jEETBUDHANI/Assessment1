"""
Main Tkinter desktop dashboard for substations telemetry monitoring.

A simple but effective fleet overview with status summary, detailed table,
drill-down capability, and voltage trend visualization using Canvas.

Run with: python main.py
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict, Optional

from models import Thresholds, HealthStatus, Substation
from service import (
    generate_demo_substations,
    generate_demo_telemetry,
    ingest_reading,
    create_fleet_snapshot,
    get_sorted_substations,
    get_voltage_trend,
    refresh_all_substations,
    reset_all_data,
)


class SubstationDashboard:
    """Main Tkinter dashboard application."""
    
    def __init__(self, root: tk.Tk):
        """Initialize dashboard UI."""
        self.root = root
        self.root.title("Substations Telemetry Dashboard")
        self.root.geometry("1200x700")
        
        # Initialize thresholds and data
        self.thresholds = Thresholds()
        self.substations = generate_demo_substations(8)
        
        # Generate demo telemetry data for each substation
        for sub in self.substations:
            generate_demo_telemetry(sub)
            # Update state based on latest reading
            refresh_all_substations([sub], self.thresholds)
        
        self.selected_station: Optional[Substation] = None
        
        # Build UI
        self._build_ui()
        self._populate_substations_table()
    
    def _build_ui(self) -> None:
        """Build the complete UI layout."""
        # Header frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="🏭 Substations Telemetry Dashboard",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Refresh and Reset buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        refresh_btn = ttk.Button(
            btn_frame,
            text="🔄 Refresh",
            command=self._refresh_data,
            width=15,
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(
            btn_frame,
            text="🔴 Reset",
            command=self._reset_data,
            width=15,
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # LEFT: Fleet summary cards and substations table
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Summary cards frame
        cards_frame = ttk.LabelFrame(left_panel, text="Fleet Summary", padding=10)
        cards_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._build_summary_cards(cards_frame)
        
        # Substations table frame
        table_frame = ttk.LabelFrame(left_panel, text="Substations", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self._build_substations_table(table_frame)
        
        # RIGHT: Detail panel and chart
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Detail frame
        detail_frame = ttk.LabelFrame(right_panel, text="Station Details", padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.detail_text = tk.Text(
            detail_frame,
            height=12,
            width=40,
            font=("Courier", 9),
            bg="#f0f0f0",
            state=tk.DISABLED,
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Chart frame
        chart_frame = ttk.LabelFrame(right_panel, text="Voltage Trend (24h)", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            chart_frame,
            height=150,
            bg="white",
            highlightthickness=1,
            highlightbackground="#ccc",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def _build_summary_cards(self, parent: ttk.Frame) -> None:
        """Build fleet summary cards."""
        snapshot = create_fleet_snapshot(self.substations)
        
        cards = [
            ("Total", str(snapshot.total_substations), "#0066cc"),
            ("🟢 Healthy", str(snapshot.healthy_count), "#00aa00"),
            ("🟡 Warning", str(snapshot.warning_count), "#ffaa00"),
            ("🔴 Critical", str(snapshot.critical_count), "#dd0000"),
        ]
        
        for label, value, color in cards:
            card = tk.Frame(parent, bg=color, height=60, relief=tk.RAISED, bd=2)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            label_widget = tk.Label(
                card,
                text=label,
                font=("Helvetica", 9),
                bg=color,
                fg="white",
            )
            label_widget.pack()
            
            value_widget = tk.Label(
                card,
                text=value,
                font=("Helvetica", 18, "bold"),
                bg=color,
                fg="white",
            )
            value_widget.pack()
    
    def _build_substations_table(self, parent: ttk.Frame) -> None:
        """Build the substations table/tree."""
        # Create treeview
        columns = ("ID", "Location", "Status", "Voltage", "Temp", "Load")
        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            height=12,
            show="headings",
        )
        
        # Define column headings and widths
        self.tree.column("ID", width=70, anchor=tk.W)
        self.tree.column("Location", width=100, anchor=tk.W)
        self.tree.column("Status", width=80, anchor=tk.CENTER)
        self.tree.column("Voltage", width=70, anchor=tk.CENTER)
        self.tree.column("Temp", width=60, anchor=tk.CENTER)
        self.tree.column("Load", width=60, anchor=tk.CENTER)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_station_selected)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _populate_substations_table(self) -> None:
        """Populate table with substation data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add sorted substations
        sorted_subs = get_sorted_substations(self.substations)
        for sub in sorted_subs:
            reading = sub.get_latest_reading()
            if reading:
                status_color = sub.state.get_status_color()
                item = self.tree.insert(
                    "",
                    "end",
                    values=(
                        sub.station_id,
                        sub.location,
                        sub.state.health.value.upper(),
                        f"{reading.voltage:.1f}V",
                        f"{reading.temperature:.1f}°C",
                        f"{reading.load:.1f}A",
                    ),
                )
                # Apply color tags (using tree item background would require ttk styling)
                self.tree.item(item, tags=(status_color,))
            else:
                self.tree.insert(
                    "",
                    "end",
                    values=(sub.station_id, sub.location, "NO DATA", "-", "-", "-"),
                )
    
    def _on_station_selected(self, event) -> None:
        """Handle substation table row selection."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        station_id = values[0]
        
        # Find substation
        for sub in self.substations:
            if sub.station_id == station_id:
                self.selected_station = sub
                self._update_detail_panel(sub)
                self._draw_voltage_chart(sub)
                break
    
    def _update_detail_panel(self, substation: Substation) -> None:
        """Update detail panel with selected substation information."""
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        reading = substation.get_latest_reading()
        if not reading:
            self.detail_text.insert(tk.END, "No data available")
            self.detail_text.config(state=tk.DISABLED)
            return
        
        detail_text = f"""
Station ID:     {substation.station_id}
Location:       {substation.location}
Status:         {substation.state.health.value.upper()}
Reading Count:  {substation.state.reading_count}

Latest Reading:
  Time:         {reading.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
  Voltage:      {reading.voltage:.2f} V
  Temperature:  {reading.temperature:.2f} °C
  Load:         {reading.load:.2f} A

Thresholds:
  Voltage:      {self.thresholds.voltage_min:.0f}-{self.thresholds.voltage_max:.0f}V
  Temp Warn:    {self.thresholds.temperature_warn:.0f}°C
  Temp Crit:    {self.thresholds.temperature_crit:.0f}°C
  Load Crit:    {self.thresholds.load_crit:.0f}A

Analysis:
""".strip()
        
        # Add analysis
        if substation.state.health == HealthStatus.CRITICAL:
            detail_text += "\n⚠️ CRITICAL CONDITIONS DETECTED"
            if reading.temperature > self.thresholds.temperature_crit:
                detail_text += f"\n  - Temperature too high: {reading.temperature:.1f}°C"
            if reading.load > self.thresholds.load_crit:
                detail_text += f"\n  - Load too high: {reading.load:.1f}A"
        elif substation.state.health == HealthStatus.WARNING:
            detail_text += "\n⚡ WARNING CONDITIONS"
            if reading.temperature > self.thresholds.temperature_warn:
                detail_text += f"\n  - Temperature rising: {reading.temperature:.1f}°C"
            if reading.load > self.thresholds.load_warn:
                detail_text += f"\n  - Load increasing: {reading.load:.1f}A"
        else:
            detail_text += "\n✓ All systems normal"
        
        self.detail_text.insert(tk.END, detail_text)
        self.detail_text.config(state=tk.DISABLED)
    
    def _draw_voltage_chart(self, substation: Substation) -> None:
        """Draw voltage trend chart on canvas."""
        self.canvas.delete("all")
        
        trend = get_voltage_trend(substation, hours=24)
        if not trend:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text="No trend data",
                font=("Helvetica", 12),
                fill="#999",
            )
            return
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 50 or canvas_height < 50:
            return
        
        # Chart margins
        margin_left = 40
        margin_right = 20
        margin_top = 20
        margin_bottom = 30
        
        chart_width = canvas_width - margin_left - margin_right
        chart_height = canvas_height - margin_top - margin_bottom
        
        # Get voltage range
        voltages = [v for _, v in trend]
        min_voltage = min(voltages)
        max_voltage = max(voltages)
        voltage_range = max_voltage - min_voltage or 1
        
        # Draw background and grid
        self.canvas.create_rectangle(
            margin_left, margin_top,
            canvas_width - margin_right, canvas_height - margin_bottom,
            outline="#ccc",
            fill="#fafafa",
        )
        
        # Draw horizontal grid lines
        for i in range(5):
            y = margin_top + (chart_height * i / 4)
            self.canvas.create_line(
                margin_left, y,
                canvas_width - margin_right, y,
                fill="#eee",
                dash=(2, 2),
            )
        
        # Plot voltage points and line
        points = []
        for idx, (_, voltage) in enumerate(trend):
            x = margin_left + (chart_width * idx / max(len(trend) - 1, 1))
            normalized = (voltage - min_voltage) / voltage_range
            y = margin_top + chart_height * (1 - normalized)
            points.append((x, y))
        
        # Draw line
        if len(points) > 1:
            self.canvas.create_line(points, fill="#0066cc", width=2)
        
        # Draw points
        for x, y in points:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#0066cc")
        
        # Draw axes
        self.canvas.create_line(
            margin_left, canvas_height - margin_bottom,
            canvas_width - margin_right, canvas_height - margin_bottom,
            width=2,
        )
        self.canvas.create_line(
            margin_left, margin_top,
            margin_left, canvas_height - margin_bottom,
            width=2,
        )
        
        # Draw y-axis labels
        for i in range(5):
            voltage = min_voltage + (voltage_range * i / 4)
            y = margin_top + chart_height * (1 - i / 4)
            self.canvas.create_text(
                margin_left - 10, y,
                text=f"{voltage:.0f}V",
                font=("Helvetica", 8),
                anchor=tk.E,
            )
        
        # Draw x-axis labels (first, middle, last)
        if len(trend) > 0:
            for idx in [0, len(trend) // 2, len(trend) - 1]:
                if idx < len(trend):
                    x = margin_left + (chart_width * idx / max(len(trend) - 1, 1))
                    time_label = trend[idx][0]
                    self.canvas.create_text(
                        x, canvas_height - margin_bottom + 15,
                        text=time_label,
                        font=("Helvetica", 8),
                        anchor=tk.N,
                    )
        
        # Title
        self.canvas.create_text(
            canvas_width // 2, 5,
            text="Voltage Trend",
            font=("Helvetica", 10, "bold"),
            anchor=tk.N,
        )
    
    def _refresh_data(self) -> None:
        """Refresh all data and redraw UI."""
        refresh_all_substations(self.substations, self.thresholds)
        self._populate_substations_table()
        
        if self.selected_station:
            self._update_detail_panel(self.selected_station)
            self._draw_voltage_chart(self.selected_station)
    
    def _reset_data(self) -> None:
        """Reset all data and regenerate demo telemetry."""
        reset_all_data(self.substations)
        
        # Regenerate demo telemetry
        for sub in self.substations:
            generate_demo_telemetry(sub)
            refresh_all_substations([sub], self.thresholds)
        
        self.selected_station = None
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.config(state=tk.DISABLED)
        self.canvas.delete("all")
        
        self._populate_substations_table()


def main():
    """Launch the dashboard application."""
    root = tk.Tk()
    app = SubstationDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
