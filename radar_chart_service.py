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
    def __init__(self, dimensions: List[str], frame: str = 'polygon'):
        if len(dimensions) < 3:
            raise ValueError("雷达图至少需要3个维度")
        self.dimensions = dimensions
        self.num_vars = len(dimensions)
        self.theta = radar_factory(self.num_vars, frame=frame)
        self.entities: List[Dict] = []
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

    def plot(self, title: str = "雷达图对比",
             rmin: float = 0, rmax: Optional[float] = None,
             rsteps: int = 5, figsize: Tuple[float, float] = (8, 8),
             show_grid: bool = True, legend_loc: str = 'lower right',
             bbox_to_anchor: Optional[Tuple[float, float]] = None) -> plt.Figure:
        if not self.entities:
            raise ValueError("请先添加至少一个实体")

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='radar')

        if show_grid:
            ax.grid(True, alpha=0.3)
        else:
            ax.grid(False)

        if rmax is None:
            all_scores = [s for e in self.entities for s in e['scores']]
            rmax = max(all_scores) * 1.1 if all_scores else 1.0

        ax.set_rlim(rmin, rmax)
        ax.set_rticks(np.linspace(rmin, rmax, rsteps + 1))
        ax.set_varlabels(self.dimensions)

        for entity in self.entities:
            scores = entity['scores']
            ax.plot(self.theta, scores, color=entity['color'],
                    linewidth=2, label=entity['name'])
            ax.fill(self.theta, scores, color=entity['color'],
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
        service = cls(dimensions=data['dimensions'])
        service.add_entities(data['entities'])
        return service
