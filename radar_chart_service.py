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

    def add_entity(self, name: str, scores: Union[List[float], Dict[str, float]],
                   color: Optional[str] = None, alpha: float = 0.25) -> None:
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

        entity_color = color if color else self.default_colors[
            len(self.entities) % len(self.default_colors)]

        self.entities.append({
            'name': name,
            'scores': scores,
            'color': entity_color,
            'alpha': alpha
        })

    def add_entities(self, entities: List[Dict]) -> None:
        for entity in entities:
            self.add_entity(
                name=entity['name'],
                scores=entity['scores'],
                color=entity.get('color'),
                alpha=entity.get('alpha', 0.25)
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
                    linewidth=2, label=entity['name'])
            ax.fill(self.theta, plot_scores, color=entity['color'],
                    alpha=entity['alpha'])

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        if bbox_to_anchor:
            ax.legend(loc=legend_loc, bbox_to_anchor=bbox_to_anchor,
                      fontsize=10)
        else:
            ax.legend(loc=legend_loc, fontsize=10)

        plt.tight_layout()
        return fig

    def save(self, output_path: str, dpi: int = 150, **plot_kwargs) -> None:
        fig = self.plot(**plot_kwargs)
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)

    def show(self, **plot_kwargs) -> None:
        fig = self.plot(**plot_kwargs)
        plt.show()
        plt.close(fig)

    def to_dict(self) -> Dict:
        return {
            'dimensions': self.dimensions,
            'normalize': self.normalize,
            'entities': [
                {
                    'name': e['name'],
                    'scores': e['scores'],
                    'color': e['color'],
                    'alpha': e['alpha']
                }
                for e in self.entities
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RadarChartService':
        service = cls(dimensions=data['dimensions'],
                      normalize=data.get('normalize', True))
        service.add_entities(data['entities'])
        return service
