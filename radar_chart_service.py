import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
from typing import List, Dict, Optional, Tuple, Union


def radar_factory(num_vars, frame='polygon'):
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):
        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars, radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown frame type: %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine = Spine(axes=self, spine_type='circle',
                             path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown frame type: %s" % frame)

    register_projection(RadarAxes)
    return theta


class RadarChartService:
    def __init__(self, dimensions: List[str], frame: str = 'polygon',
                 normalize: bool = True):
        if len(dimensions) < 3:
            raise ValueError("雷达图至少需要3个维度")
        self.dimensions = dimensions
        self.num_vars = len(dimensions)
        self.theta = radar_factory(self.num_vars, frame=frame)
        self.entities: List[Dict] = []
        self.normalize = normalize
        self._norm_ranges: Optional[Dict[str, Tuple[float, float]]] = None
        self.default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                               '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                               '#bcbd22', '#17becf']
        self.group_palettes = [
            ['#1f77b4', '#4a90c9', '#7bb0db', '#a9cced'],
            ['#ff7f0e', '#ffa14d', '#ffc280', '#ffd9b3'],
            ['#2ca02c', '#55b855', '#7fce7f', '#a8e1a8'],
            ['#d62728', '#e15a5a', '#ec8c8c', '#f3bdbd'],
            ['#9467bd', '#ab89cd', '#c3acde', '#dacfee'],
            ['#8c564b', '#a57a71', '#be9e97', '#d5c1bd'],
            ['#e377c2', '#ea99d1', '#f1bbe0', '#f7dde7'],
            ['#17becf', '#45cfdb', '#73dde4', '#a2ebef'],
        ]
        self.group_linestyles = ['-', '--', '-.', ':',
                                 (0, (5, 1)), (0, (3, 5, 1, 5)),
                                 (0, (3, 1, 1, 1)), (0, (1, 1))]
        self.groups: Dict[str, Dict] = {}
        self._group_counter = 0

    def add_entity(self, name: str, scores: Union[List[float], Dict[str, float]],
                   color: Optional[str] = None, alpha: float = 0.25,
                   group: Optional[str] = None,
                   linestyle: Optional[Union[str, Tuple]] = None) -> None:
        if isinstance(scores, dict):
            score_list = []
            for dim in self.dimensions:
                if dim not in scores:
                    raise ValueError(f"实体 {name} 缺少维度 {dim} 的分数")
                score_list.append(scores[dim])
            scores = score_list

        if len(scores) != self.num_vars:
            raise ValueError(
                f"分数数量 ({len(scores)}) 与维度数量 ({self.num_vars}) 不匹配")

        entity_color = color
        entity_linestyle = linestyle

        if group is not None:
            if group not in self.groups:
                self._register_group(group)
            gdata = self.groups[group]
            idx_in_group = sum(1 for e in self.entities if e.get('group') == group)
            if entity_color is None:
                palette = gdata['palette']
                entity_color = palette[idx_in_group % len(palette)]
            if entity_linestyle is None:
                entity_linestyle = gdata['linestyle']
        else:
            if entity_color is None:
                entity_color = self.default_colors[
                    len(self.entities) % len(self.default_colors)]
            if entity_linestyle is None:
                entity_linestyle = '-'

        self.entities.append({
            'name': name,
            'scores': scores,
            'color': entity_color,
            'alpha': alpha,
            'group': group,
            'linestyle': entity_linestyle
        })

    def _register_group(self, group_name: str) -> None:
        idx = self._group_counter
        palette = self.group_palettes[idx % len(self.group_palettes)]
        linestyle = self.group_linestyles[idx % len(self.group_linestyles)]
        self.groups[group_name] = {
            'name': group_name,
            'palette': palette,
            'linestyle': linestyle,
            'base_color': palette[0]
        }
        self._group_counter += 1

    def add_group(self, group_name: str,
                  entities: List[Dict],
                  palette: Optional[List[str]] = None,
                  linestyle: Optional[Union[str, Tuple]] = None) -> None:
        if group_name in self.groups:
            raise ValueError(f"分组 {group_name} 已存在")
        self._register_group(group_name)
        if palette is not None:
            self.groups[group_name]['palette'] = palette
            self.groups[group_name]['base_color'] = palette[0]
        if linestyle is not None:
            self.groups[group_name]['linestyle'] = linestyle
        for entity in entities:
            self.add_entity(
                name=entity['name'],
                scores=entity['scores'],
                color=entity.get('color'),
                alpha=entity.get('alpha', 0.25),
                group=group_name,
                linestyle=entity.get('linestyle')
            )

    def add_entity_to_group(self, group_name: str, name: str,
                            scores: Union[List[float], Dict[str, float]],
                            color: Optional[str] = None,
                            alpha: float = 0.25,
                            linestyle: Optional[Union[str, Tuple]] = None
                            ) -> None:
        if group_name not in self.groups:
            self._register_group(group_name)
        self.add_entity(name=name, scores=scores, color=color,
                        alpha=alpha, group=group_name, linestyle=linestyle)

    def add_entities(self, entities: List[Dict]) -> None:
        for entity in entities:
            self.add_entity(
                name=entity['name'],
                scores=entity['scores'],
                color=entity.get('color'),
                alpha=entity.get('alpha', 0.25),
                group=entity.get('group'),
                linestyle=entity.get('linestyle')
            )

    def _compute_norm_ranges(self) -> Dict[str, Tuple[float, float]]:
        ranges = {}
        for i, dim in enumerate(self.dimensions):
            dim_values = [e['scores'][i] for e in self.entities]
            ranges[dim] = (min(dim_values), max(dim_values))
        return ranges

    def _normalize_scores(self, scores: List[float],
                          ranges: Dict[str, Tuple[float, float]]) -> List[float]:
        normalized = []
        for i, dim in enumerate(self.dimensions):
            dmin, dmax = ranges[dim]
            if dmax == dmin:
                normalized.append(0.5)
            else:
                normalized.append((scores[i] - dmin) / (dmax - dmin))
        return normalized

    def _denormalize_tick(self, norm_val: float,
                          dmin: float, dmax: float) -> float:
        if dmax == dmin:
            return dmin
        return dmin + norm_val * (dmax - dmin)

    def plot(self, title: str = "雷达图对比",
             rmin: Optional[float] = None, rmax: Optional[float] = None,
             rsteps: int = 5, figsize: Tuple[float, float] = (8, 8),
             show_grid: bool = True, legend_loc: str = 'lower right',
             bbox_to_anchor: Optional[Tuple[float, float]] = None,
             normalize: Optional[bool] = None) -> plt.Figure:
        if not self.entities:
            raise ValueError("请先添加至少一个实体")

        use_normalize = normalize if normalize is not None else self.normalize
        ranges = self._compute_norm_ranges() if use_normalize else None

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='radar')

        if show_grid:
            ax.grid(True, alpha=0.3)
        else:
            ax.grid(False)

        if use_normalize:
            ax.set_rlim(0, 1)
            tick_positions = np.linspace(0, 1, rsteps + 1)
            all_ticks = []
            for pos in tick_positions:
                per_dim = []
                for dim in self.dimensions:
                    dmin, dmax = ranges[dim]
                    per_dim.append(self._denormalize_tick(pos, dmin, dmax))
                all_ticks.append(per_dim)
            dim_tick_labels = []
            for i, dim in enumerate(self.dimensions):
                labels = [f"{t[i]:.1f}" for t in all_ticks]
                dim_tick_labels.append(f"{dim}\n({'/'.join(labels[1:])})")
            ax.set_rticks(tick_positions)
            ax.set_yticklabels([f"{v:.1f}" for v in tick_positions], fontsize=7)
            ax.set_varlabels(dim_tick_labels)
        else:
            if rmax is None:
                all_scores = [s for e in self.entities for s in e['scores']]
                rmax = max(all_scores) * 1.1 if all_scores else 1.0
            if rmin is None:
                rmin = 0
            ax.set_rlim(rmin, rmax)
            ax.set_rticks(np.linspace(rmin, rmax, rsteps + 1))
            ax.set_varlabels(self.dimensions)

        for entity in self.entities:
            scores = entity['scores']
            plot_scores = self._normalize_scores(scores, ranges) if use_normalize else scores
            ax.plot(self.theta, plot_scores, color=entity['color'],
                    linewidth=2, linestyle=entity.get('linestyle', '-'),
                    label=entity['name'])
            ax.fill(self.theta, plot_scores, color=entity['color'],
                    alpha=entity['alpha'])

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        if self.groups:
            handles, labels = ax.get_legend_handles_labels()
            new_handles = []
            new_labels = []
            current_group = None
            grouped_entities = {}
            for entity in self.entities:
                g = entity.get('group')
                if g not in grouped_entities:
                    grouped_entities[g] = []
                grouped_entities[g].append(entity)
            for gname, gents in grouped_entities.items():
                if gname is not None and gname in self.groups:
                    gdata = self.groups[gname]
                    proxy_line = plt.Line2D(
                        [0], [0], color=gdata['base_color'],
                        linestyle=gdata['linestyle'],
                        linewidth=3, marker='', markersize=0)
                    new_handles.append(proxy_line)
                    new_labels.append(f'【{gname}】')
                for e in gents:
                    idx = [i for i, x in enumerate(self.entities) if x is e][0]
                    if idx < len(handles):
                        new_handles.append(handles[idx])
                        new_labels.append(f"  {labels[idx]}")
            ax.legend(new_handles, new_labels,
                      loc=legend_loc, bbox_to_anchor=bbox_to_anchor,
                      fontsize=10, handlelength=2.5)
        else:
            if bbox_to_anchor:
                ax.legend(loc=legend_loc, bbox_to_anchor=bbox_to_anchor,
                          fontsize=10)
            else:
                ax.legend(loc=legend_loc, fontsize=10)

        plt.tight_layout()
        return fig

    def _render_single_axes(self, ax, entities: List[Dict],
                            ranges: Optional[Dict[str, Tuple[float, float]]],
                            use_normalize: bool, rmin, rmax, rsteps,
                            sub_title: str):
        if use_normalize:
            ax.set_rlim(0, 1)
            tick_positions = np.linspace(0, 1, rsteps + 1)
            all_ticks = []
            for pos in tick_positions:
                per_dim = []
                for dim in self.dimensions:
                    dmin, dmax = ranges[dim]
                    per_dim.append(self._denormalize_tick(pos, dmin, dmax))
                all_ticks.append(per_dim)
            dim_tick_labels = []
            for i, dim in enumerate(self.dimensions):
                labels = [f"{t[i]:.1f}" for t in all_ticks]
                dim_tick_labels.append(f"{dim}\n({'/'.join(labels[1:])})")
            ax.set_rticks(tick_positions)
            ax.set_yticklabels([f"{v:.1f}" for v in tick_positions], fontsize=6)
            ax.set_varlabels(dim_tick_labels)
        else:
            if rmax is None:
                all_scores = [s for e in entities for s in e['scores']]
                rmax = max(all_scores) * 1.1 if all_scores else 1.0
            if rmin is None:
                rmin = 0
            ax.set_rlim(rmin, rmax)
            ax.set_rticks(np.linspace(rmin, rmax, rsteps + 1))
            ax.set_varlabels(self.dimensions)

        grouped = {}
        for e in entities:
            g = e.get('group')
            if g not in grouped:
                grouped[g] = []
            grouped[g].append(e)

        handles = []
        labels_list = []
        for gname, gents in grouped.items():
            if gname is not None and gname in self.groups:
                gdata = self.groups[gname]
                proxy = plt.Line2D([0], [0], color=gdata['base_color'],
                                   linestyle=gdata['linestyle'],
                                   linewidth=3)
                handles.append(proxy)
                labels_list.append(f'【{gname}】')
            for e in gents:
                scores = e['scores']
                ps = self._normalize_scores(scores, ranges) if use_normalize else scores
                lines_before = set(id(l) for l in ax.get_lines())
                ax.plot(self.theta, ps, color=e['color'],
                        linewidth=2, linestyle=e.get('linestyle', '-'))
                new_lines = [l for l in ax.get_lines()
                             if id(l) not in lines_before]
                line = new_lines[-1] if new_lines else plt.Line2D(
                    [0], [0], color=e['color'],
                    linestyle=e.get('linestyle', '-'), linewidth=2)
                ax.fill(self.theta, ps, color=e['color'], alpha=e['alpha'])
                handles.append(line)
                labels_list.append(f"  {e['name']}")

        ax.set_title(sub_title, fontsize=12, fontweight='bold', pad=15)
        return handles, labels_list

    def plot_multi(self, layouts: List[Dict],
                   ncols: int = 2,
                   figsize: Tuple[float, float] = (12, 10),
                   rmin=None, rmax=None, rsteps=5,
                   show_grid=True,
                   normalize: Optional[bool] = None,
                   legend_loc='lower right',
                   share_legend: bool = False,
                   super_title: Optional[str] = None) -> plt.Figure:
        use_normalize = normalize if normalize is not None else self.normalize
        all_entities = list(self.entities)
        if use_normalize:
            ranges = self._compute_norm_ranges()
        else:
            ranges = None

        n = len(layouts)
        ncols = min(ncols, n)
        nrows = (n + ncols - 1) // ncols

        fig = plt.figure(figsize=figsize)
        if super_title:
            fig.suptitle(super_title, fontsize=16, fontweight='bold', y=1.02)

        all_handles = []
        all_labels = []
        seen = set()

        for i, layout in enumerate(layouts):
            ax = fig.add_subplot(nrows, ncols, i + 1, projection='radar')
            if show_grid:
                ax.grid(True, alpha=0.3)
            else:
                ax.grid(False)

            filter_fn = layout.get('filter')
            if filter_fn:
                sub_entities = [e for e in all_entities if filter_fn(e)]
            else:
                groups = layout.get('groups')
                names = layout.get('names')
                sub_entities = []
                for e in all_entities:
                    if groups and e.get('group') in groups:
                        sub_entities.append(e)
                    elif names and e['name'] in names:
                        sub_entities.append(e)
                if not groups and not names:
                    sub_entities = list(all_entities)

            sub_title = layout.get('title', f'第{i+1}组')
            handles, labels = self._render_single_axes(
                ax, sub_entities, ranges, use_normalize,
                rmin, rmax, rsteps, sub_title)

            if share_legend:
                for h, lb in zip(handles, labels):
                    if lb not in seen:
                        seen.add(lb)
                        all_handles.append(h)
                        all_labels.append(lb)
            else:
                ax.legend(handles, labels, loc=legend_loc,
                          fontsize=8, handlelength=2)

        if share_legend and all_handles:
            fig.legend(all_handles, all_labels, loc='center right',
                       fontsize=9, handlelength=2.5,
                       bbox_to_anchor=(1.02, 0.5))

        plt.tight_layout()
        return fig

    def save_multi(self, output_path: str, layouts: List[Dict],
                   dpi: int = 150, **plot_kwargs) -> None:
        fig = self.plot_multi(layouts, **plot_kwargs)
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

    def save(self, output_path: str, dpi: int = 150, **plot_kwargs) -> None:
        fig = self.plot(**plot_kwargs)
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

    def show(self, **plot_kwargs) -> None:
        fig = self.plot(**plot_kwargs)
        plt.show()
        plt.close(fig)

    def to_dict(self) -> Dict:
        groups_info = {}
        for gname, gdata in self.groups.items():
            groups_info[gname] = {
                'palette': gdata['palette'],
                'linestyle': str(gdata['linestyle']) if not isinstance(
                    gdata['linestyle'], (list, tuple)) else list(gdata['linestyle']),
                'base_color': gdata['base_color']
            }
        return {
            'dimensions': self.dimensions,
            'normalize': self.normalize,
            'groups': groups_info,
            'entities': [
                {
                    'name': e['name'],
                    'scores': e['scores'],
                    'color': e['color'],
                    'alpha': e['alpha'],
                    'group': e.get('group'),
                    'linestyle': str(e.get('linestyle')) if (
                        e.get('linestyle') is not None
                        and not isinstance(e['linestyle'], (list, tuple))
                    ) else (list(e['linestyle']) if isinstance(
                        e['linestyle'], (list, tuple)) else None)
                }
                for e in self.entities
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RadarChartService':
        service = cls(dimensions=data['dimensions'],
                      normalize=data.get('normalize', True))
        for gname, ginfo in data.get('groups', {}).items():
            service.groups[gname] = {
                'name': gname,
                'palette': ginfo['palette'],
                'linestyle': ginfo['linestyle'],
                'base_color': ginfo['base_color']
            }
            service._group_counter += 1
        service.add_entities(data['entities'])
        return service
