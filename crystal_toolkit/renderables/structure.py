from collections import defaultdict
from itertools import combinations

import numpy as np
from pymatgen.core.structure import Structure

from crystal_toolkit.core.scene import Scene
from crystal_toolkit.core.legend import Legend

from typing import Optional


def _get_sites_to_draw(self, draw_image_atoms=True):
    """
    Returns a list of site indices and image vectors.
    """

    sites_to_draw = [(idx, (0, 0, 0)) for idx in range(len(self))]

    if draw_image_atoms:

        for idx, site in enumerate(self):

            zero_elements = [
                idx
                for idx, f in enumerate(site.frac_coords)
                if np.allclose(f, 0, atol=0.05)
            ]

            coord_permutations = [
                x
                for l in range(1, len(zero_elements) + 1)
                for x in combinations(zero_elements, l)
            ]

            for perm in coord_permutations:
                sites_to_draw.append(
                    (idx, (int(0 in perm), int(1 in perm), int(2 in perm)))
                )

            one_elements = [
                idx
                for idx, f in enumerate(site.frac_coords)
                if np.allclose(f, 1, atol=0.05)
            ]

            coord_permutations = [
                x
                for l in range(1, len(one_elements) + 1)
                for x in combinations(one_elements, l)
            ]

            for perm in coord_permutations:
                sites_to_draw.append(
                    (idx, (-int(0 in perm), -int(1 in perm), -int(2 in perm)))
                )

    return set(sites_to_draw)


def get_structure_scene(
    self, draw_image_atoms=True, legend: Optional[Legend] = None, origin=None,
) -> Scene:

    origin = origin or list(-self.lattice.get_cartesian_coords([0.5, 0.5, 0.5]))

    legend = legend or Legend(self)

    primitives = defaultdict(list)

    sites_to_draw = self._get_sites_to_draw(draw_image_atoms=draw_image_atoms)

    for (idx, jimage) in sites_to_draw:

        site_scene = self[idx].get_scene(origin=origin, legend=legend)
        for scene in site_scene.contents:
            primitives[scene.name] += scene.contents

    primitives["unit_cell"].append(self.lattice.get_scene(origin=origin))

    return Scene(
        name=self.composition.reduced_formula,
        contents=[Scene(name=k, contents=v) for k, v in primitives.items()],
        origin=origin,
    )


Structure._get_sites_to_draw = _get_sites_to_draw
Structure.get_scene = get_structure_scene
