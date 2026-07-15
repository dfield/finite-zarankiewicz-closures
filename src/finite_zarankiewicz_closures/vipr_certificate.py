"""Integrity and model-binding checks for the two ``Z(10,23)`` VIPR covers."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
import itertools
import json
import lzma
from pathlib import Path
import re
from typing import Any, BinaryIO, Iterator, Mapping, TextIO


class ViprCertificateError(ValueError):
    """Raised when a VIPR cover, release index, or embedded model is invalid."""


HEX_DIGEST = re.compile(r"[0-9a-f]{64}")
TRIPLES = tuple(itertools.combinations(range(10), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
FIXED_TRIPLE_INDEX = TRIPLE_INDEX[(0, 1, 2)]
B_GENERATORS = (
    (0, 1),
    (1, 2),
    *zip(range(3, 9), range(4, 10)),
)
FIXED_ROWS = (0, 1, 2)
FREE_ROWS = tuple(range(3, 10))
FIXED_MASK = sum(1 << row for row in FIXED_ROWS)
SUPPORT_PERMUTATIONS = tuple(itertools.permutations(range(3)))
PATTERN_MAPS = tuple(
    tuple(
        sum(((old >> permutation[new]) & 1) << new for new in range(3))
        for old in range(8)
    )
    for permutation in SUPPORT_PERMUTATIONS
)

VIPR_SOURCE_COMMIT = "30f2951d1e90e47afa821bdd1b12b82246656c42"
VIPR_SOURCE_SHA256 = "7d20cd04ba11488fbc8ed3fbabfdfa513e161a0c36b75220927f55051614ed2f"
SCIP_ARCHIVE_SHA256 = "ddbb7129bdb83f8f70ed26391d206fd1658139e44c7c7fd7d73a1e4cefbca94f"
MODEL_GENERATOR_SHA256 = "389a7a80d8f3aaa4474246ceeb01d3b7cf17eba8c0769e64a1555d7fdd84ead0"

PROFILE_DATA: dict[str, dict[str, Any]] = {
    "3x1,4x4,5x14,6x4": {
        "name": "B",
        "slug": "3d1_4d4_5d14_6d4",
        "manifest": "profile-b-vipr-final-manifest.json",
        "manifest_sha256": "3c46aa06a9f7a33ef42e5328e738f4ecfdcb26f60603b1a85ad01145cbc500af",
        "catalog": "profile-b-deficit-orbits.jsonl",
        "catalog_sha256": "f29131310a1518e4b65fc3b831f63cd88bff3334fb7424435ad7e530daceed42",
        "catalog_metadata": "profile-b-deficit-orbits.json",
        "catalog_metadata_sha256": "72c481950db00778c97ec29d1ffd7185e468bebe2bc751f38f4743e78df634c5",
        "release": "3d1_4d4_5d14_6d4.vipr-certificates.release.json",
        "orbits": 209,
        "raw_states": 295_001,
        "constraints": 860,
        "equalities": 123,
    },
    "3x1,4x3,5x16,6x3": {
        "name": "C",
        "slug": "3d1_4d3_5d16_6d3",
        "manifest": "profile-c-vipr-final-manifest.json",
        "manifest_sha256": "30fd5b8fba89a4d51fcac8e37be2e34535606be36fc19f651fbfa990ef419ded",
        "catalog": "profile-c-degree6-orbits.jsonl",
        "catalog_sha256": "1bbdaf13f43bfeccbcf8c52d7890ba9494a89252603294f08c5cb2b640dd331b",
        "catalog_metadata": "profile-c-degree6-orbits.json",
        "catalog_metadata_sha256": "6184d0ac76602ff054602a7cb71eee284ad512e459f2f4488bdb988ff1a4677f",
        "release": "3d1_4d3_5d16_6d3.vipr-certificates.release.json",
        "orbits": 236,
        "raw_states": 950_250,
        "constraints": 863,
        "equalities": 6,
        "formula_aggregate_sha256": "c785946067220c2bd9a89cd28d90928cbfdc5287f0334ed9aada8823cce0c404",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path, expected_sha256: str) -> Mapping[str, Any]:
    if not path.is_file() or _sha256(path) != expected_sha256:
        raise ViprCertificateError(f"VIPR artifact hash mismatch: {path}")
    value = json.loads(path.read_text(encoding="ascii"))
    if not isinstance(value, dict):
        raise ViprCertificateError(f"VIPR JSON artifact is not an object: {path}")
    return value


def _load_jsonl(path: Path, expected_sha256: str) -> list[Mapping[str, Any]]:
    if not path.is_file() or _sha256(path) != expected_sha256:
        raise ViprCertificateError(f"VIPR catalog hash mismatch: {path}")
    records = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ViprCertificateError(f"malformed VIPR catalog at {path}:{line_number}") from error
        if not isinstance(record, dict):
            raise ViprCertificateError(f"non-object VIPR catalog record at {path}:{line_number}")
        records.append(record)
    return records


def _b_transformations() -> tuple[tuple[int, ...], ...]:
    result = []
    for first, second in B_GENERATORS:
        moved = []
        for triple in TRIPLES:
            image = tuple(
                sorted(
                    second if row == first else first if row == second else row
                    for row in triple
                )
            )
            moved.append(TRIPLE_INDEX[image])
        result.append(tuple(moved))
    return tuple(result)


@lru_cache(maxsize=1)
def _expected_b_orbits() -> tuple[tuple[tuple[int, int, int], int], ...]:
    transformations = _b_transformations()
    seen: set[tuple[int, int, int]] = set()
    result: list[tuple[tuple[int, int, int], int]] = []
    raw_states = 0
    for state in itertools.combinations_with_replacement(range(len(TRIPLES)), 3):
        if state[0] == state[2] or state.count(FIXED_TRIPLE_INDEX) > 1:
            continue
        raw_states += 1
        if state in seen:
            continue
        orbit = {state}
        frontier = [state]
        while frontier:
            current = frontier.pop()
            for transformation in transformations:
                image = tuple(sorted(transformation[index] for index in current))
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        seen.update(orbit)
        result.append((min(orbit), len(orbit)))
    result.sort()
    if raw_states != 295_001 or len(seen) != raw_states or len(result) != 209:
        raise ViprCertificateError("independent profile-B orbit census failed")
    return tuple(result)


def _pattern_counts(masks: tuple[int, int, int], rows: tuple[int, ...]) -> tuple[int, ...]:
    counts = [0] * 8
    for row in rows:
        pattern = sum(((mask >> row) & 1) << index for index, mask in enumerate(masks))
        counts[pattern] += 1
    return tuple(counts)


def _canonical_c_signature(masks: tuple[int, int, int]) -> tuple[int, ...]:
    fixed = _pattern_counts(masks, FIXED_ROWS)
    free = _pattern_counts(masks, FREE_ROWS)
    signatures = []
    for pattern_map in PATTERN_MAPS:
        remapped_fixed = [0] * 8
        remapped_free = [0] * 8
        for old, new in enumerate(pattern_map):
            remapped_fixed[new] = fixed[old]
            remapped_free[new] = free[old]
        signatures.append((*remapped_fixed, *remapped_free))
    return min(signatures)


def _admissible_c(masks: tuple[int, int, int]) -> bool:
    return (
        masks[0] != masks[2]
        and bin(masks[0] & masks[1] & masks[2]).count("1") < 3
        and sum(mask & FIXED_MASK == FIXED_MASK for mask in masks) <= 1
    )


@lru_cache(maxsize=1)
def _expected_c_orbits() -> dict[tuple[int, ...], tuple[tuple[int, int, int], int]]:
    degree_six_masks = tuple(
        sum(1 << row for row in rows)
        for rows in itertools.combinations(range(10), 6)
    )
    result: dict[tuple[int, ...], tuple[tuple[int, int, int], int]] = {}
    raw_states = 0
    for indices in itertools.combinations_with_replacement(range(len(degree_six_masks)), 3):
        masks = tuple(degree_six_masks[index] for index in indices)
        if not _admissible_c(masks):
            continue
        raw_states += 1
        signature = _canonical_c_signature(masks)
        if signature in result:
            representative, count = result[signature]
            result[signature] = (representative, count + 1)
        else:
            result[signature] = (masks, 1)
    if raw_states != 950_250 or len(result) != 236:
        raise ViprCertificateError("independent profile-C orbit census failed")
    return result


def _verify_catalog(profile: str, records: list[Mapping[str, Any]]) -> None:
    data = PROFILE_DATA[profile]
    if [record.get("index") for record in records] != list(range(data["orbits"])):
        raise ViprCertificateError(f"noncanonical orbit indices for profile {data['name']}")
    if profile == "3x1,4x4,5x14,6x4":
        expected = _expected_b_orbits()
        observed = []
        for record in records:
            state = tuple(
                sorted(TRIPLE_INDEX[tuple(triple)] for triple in record["deficit_triples"])
            )
            observed.append((state, int(record["orbit_size"])))
        if tuple(observed) != expected:
            raise ViprCertificateError("profile-B catalog differs from the independent orbit cover")
        return

    expected_c = _expected_c_orbits()
    observed_signatures: set[tuple[int, ...]] = set()
    for record in records:
        masks = tuple(int(mask) for mask in record["degree_six_support_masks"])
        signature_record = record["canonical_signature"]
        signature = tuple(signature_record["fixed_block_pattern_counts"]) + tuple(
            signature_record["free_block_pattern_counts"]
        )
        if (
            not _admissible_c(masks)
            or _canonical_c_signature(masks) != signature
            or signature not in expected_c
            or expected_c[signature] != (masks, int(record["orbit_size"]))
            or signature in observed_signatures
        ):
            raise ViprCertificateError("profile-C catalog differs from the independent orbit cover")
        observed_signatures.add(signature)
    if observed_signatures != set(expected_c):
        raise ViprCertificateError("profile-C catalog omits an orbit")


@lru_cache(maxsize=None)
def _model_generator(root: Path) -> Any:
    path = root / "search" / "z10_23_vipr" / "column_count_opb.py"
    if not path.is_file() or _sha256(path) != MODEL_GENERATOR_SHA256:
        raise ViprCertificateError("the exact OPB generator hash changed")
    spec = importlib.util.spec_from_file_location("z10_23_vipr_model", path)
    if spec is None or spec.loader is None:
        raise ViprCertificateError("could not load the exact OPB generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_vipr_leaf_formula(
    root: Path,
    profile: str,
    record: Mapping[str, Any],
) -> tuple[str, Mapping[str, Any]]:
    """Regenerate one exact OPB leaf from its orbit representative."""

    generator = _model_generator(root)
    if profile == "3x1,4x4,5x14,6x4":
        deficits = {triple: 0 for triple in TRIPLES}
        for triple in record["deficit_triples"]:
            deficits[tuple(triple)] += 1
        text, mapping, metadata = generator.build(
            "B",
            deficit_links="none",
            row_symmetry="none",
            deficit_incidence_links=False,
            triple_deficits=deficits,
        )
    elif profile == "3x1,4x3,5x16,6x3":
        masks = tuple(int(mask) for mask in record["degree_six_support_masks"])
        text, mapping, metadata = generator.build(
            "C",
            deficit_links="none",
            row_symmetry="none",
            deficit_incidence_links=False,
            complete_degree_supports=masks,
        )
    else:
        raise ViprCertificateError(f"unexpected VIPR profile: {profile}")
    data = PROFILE_DATA[profile]
    if (
        len(mapping) != 1344
        or metadata.get("variables") != 1344
        or metadata.get("constraints") != data["constraints"]
        or metadata.get("equalities") != data["equalities"]
    ):
        raise ViprCertificateError("regenerated OPB leaf has unexpected dimensions")
    return text, metadata


def _verify_release(
    release: Mapping[str, Any],
    manifest_path: Path,
    manifest: Mapping[str, Any],
    data: Mapping[str, Any],
) -> int:
    parts = release.get("parts")
    if (
        release.get("schema_version") != 1
        or release.get("format") != "TAR+VIPR+xz-members+github-release-parts"
        or release.get("profile") != manifest["profile"]
        or release.get("slug") != data["slug"]
        or release.get("member_count") != data["orbits"]
        or release.get("cover_manifest")
        != {
            "file": manifest_path.name,
            "bytes": manifest_path.stat().st_size,
            "sha256": data["manifest_sha256"],
        }
        or release.get("release")
        != {
            "repository": "dfield/finite-zarankiewicz-closures",
            "tag": "z10-23-certificate-v1",
        }
        or release.get("archive")
        != {
            "format": "deterministic POSIX.1-1988 ustar",
            "member_compression": "xz",
            "member_name_pattern": "proofs/leaf-%06d.vipr.xz",
            "mode": "0444",
            "mtime": 0,
            "uid": 0,
            "gid": 0,
        }
        or not isinstance(parts, list)
        or not parts
    ):
        raise ViprCertificateError(f"invalid VIPR release sidecar for profile {data['name']}")
    expected_names = [
        f"{data['slug']}.vipr-certificates.tar.part-{index:02d}"
        for index in range(len(parts))
    ]
    if [part.get("name") for part in parts] != expected_names:
        raise ViprCertificateError("VIPR release parts are not canonically named")
    total = 0
    for part in parts:
        if (
            not isinstance(part.get("bytes"), int)
            or not 0 < part["bytes"] < 2_000_000_000
            or not isinstance(part.get("sha256"), str)
            or HEX_DIGEST.fullmatch(part["sha256"]) is None
        ):
            raise ViprCertificateError("invalid VIPR release part metadata")
        total += part["bytes"]
    if (
        total != release.get("bytes")
        or not isinstance(release.get("sha256"), str)
        or HEX_DIGEST.fullmatch(release["sha256"]) is None
    ):
        raise ViprCertificateError("invalid VIPR release stream metadata")
    certificate_bytes = sum(
        int(leaf["artifacts"]["certificate.vipr.xz"]["bytes"])
        for leaf in manifest["leaves"]
    )
    if release.get("certificate_bytes") != certificate_bytes:
        raise ViprCertificateError("VIPR release certificate byte count is wrong")
    return total


def verify_vipr_cover(root: Path, profile: str) -> dict[str, Any]:
    """Verify a complete orbit cover, every leaf formula hash, and its release index."""

    if profile not in PROFILE_DATA:
        raise ViprCertificateError(f"unexpected VIPR profile: {profile}")
    data = PROFILE_DATA[profile]
    directory = root / "certificates" / "z10_23" / "vipr"
    manifest_path = directory / data["manifest"]
    manifest = _load_json(manifest_path, data["manifest_sha256"])
    catalog = _load_jsonl(directory / data["catalog"], data["catalog_sha256"])
    catalog_metadata = _load_json(
        directory / data["catalog_metadata"], data["catalog_metadata_sha256"]
    )
    release_path = directory / data["release"]
    if not release_path.is_file():
        raise ViprCertificateError(f"missing VIPR release sidecar: {release_path}")
    release = json.loads(release_path.read_text(encoding="ascii"))
    if not isinstance(release, dict):
        raise ViprCertificateError("VIPR release sidecar is not an object")

    if (
        manifest.get("schema_version") != 1
        or manifest.get("status") != "COMPLETE_VERIFIED_ORBIT_COVER"
        or manifest.get("profile") != profile
        or manifest.get("verified_leaf_count") != data["orbits"]
        or manifest.get("theorem_obligation")
        != f"profile {profile} is impossible at 113 ones"
        or manifest.get("tools")
        != {
            "scip_archive_sha256": SCIP_ARCHIVE_SHA256,
            "vipr_source_commit": VIPR_SOURCE_COMMIT,
            "vipr_source_sha256": VIPR_SOURCE_SHA256,
        }
    ):
        raise ViprCertificateError(f"invalid aggregate VIPR manifest for profile {data['name']}")
    cover = manifest.get("cover")
    if (
        not isinstance(cover, dict)
        or cover.get("orbit_count") != data["orbits"]
        or cover.get("raw_state_count") != data["raw_states"]
        or cover.get("orbit_size_sum") != data["raw_states"]
        or cover.get("catalog", {}).get("sha256") != data["catalog_sha256"]
        or cover.get("catalog_metadata", {}).get("sha256")
        != data["catalog_metadata_sha256"]
        or catalog_metadata.get("status") != "COMPLETE_ORBIT_COVER"
        or catalog_metadata.get("catalog", {}).get("sha256") != data["catalog_sha256"]
    ):
        raise ViprCertificateError(f"incomplete VIPR cover metadata for profile {data['name']}")
    _verify_catalog(profile, catalog)

    leaves = manifest.get("leaves")
    if (
        not isinstance(leaves, list)
        or len(leaves) != data["orbits"]
        or [leaf.get("index") for leaf in leaves] != list(range(data["orbits"]))
    ):
        raise ViprCertificateError("aggregate VIPR leaves are not complete and canonical")

    formula_aggregate = hashlib.sha256()
    certificate_bytes = 0
    for index, (record, leaf) in enumerate(zip(catalog, leaves)):
        if int(leaf.get("orbit_size", -1)) != int(record["orbit_size"]):
            raise ViprCertificateError(f"orbit-size mismatch at VIPR leaf {index}")
        if profile == "3x1,4x4,5x14,6x4":
            if leaf.get("deficit_triples") != record.get("deficit_triples"):
                raise ViprCertificateError(f"profile-B representative mismatch at leaf {index}")
        elif leaf.get("degree_six_support_masks") != record.get("degree_six_support_masks"):
            raise ViprCertificateError(f"profile-C representative mismatch at leaf {index}")
        if (
            leaf.get("certificate_features")
            != {"AggrRow_": 0, "lin incomplete": 0, "lin weak": 0}
            or leaf.get("checker", {}).get("returncode") != 0
            or leaf.get("checker", {}).get("externally_timed_out") is not False
            or leaf.get("solver", {}).get("returncode") != 0
            or leaf.get("solver", {}).get("externally_timed_out") is not False
        ):
            raise ViprCertificateError(f"unverified or incomplete VIPR leaf {index}")
        commands = leaf["solver"].get("commands", [])
        for required in (
            "set exact enable TRUE",
            "set presolving emphasis off",
            "set conflict enable FALSE",
        ):
            if required not in commands:
                raise ViprCertificateError(f"unsafe SCIP certificate mode at leaf {index}")
        formula_text, _ = render_vipr_leaf_formula(root, profile, record)
        formula_payload = formula_text.encode("ascii")
        formula_sha = hashlib.sha256(formula_payload).hexdigest()
        if leaf.get("formula") != {
            "file": f"leaf-{index:06d}.opb",
            "bytes": len(formula_payload),
            "sha256": formula_sha,
        }:
            raise ViprCertificateError(f"regenerated OPB formula mismatch at leaf {index}")
        formula_aggregate.update(f"{index}:{formula_sha}\n".encode("ascii"))
        artifacts = leaf.get("artifacts")
        if not isinstance(artifacts, dict) or set(artifacts) != {
            "certificate.vipr.xz",
            "certificate.vipr_ori.xz",
            "scip.log.xz",
            "viprchk.log.xz",
        }:
            raise ViprCertificateError(f"incomplete VIPR artifact set at leaf {index}")
        for name, artifact in artifacts.items():
            if (
                artifact.get("file") != name
                or artifact.get("server_side_encryption") != "AES256"
                or not isinstance(artifact.get("bytes"), int)
                or artifact["bytes"] <= 0
                or not isinstance(artifact.get("sha256"), str)
                or HEX_DIGEST.fullmatch(artifact["sha256"]) is None
                or not artifact.get("key", "").endswith(
                    f"/leaf-{index:06d}/{name}"
                )
            ):
                raise ViprCertificateError(f"invalid {name} metadata at leaf {index}")
        certificate_bytes += artifacts["certificate.vipr.xz"]["bytes"]

    if profile == "3x1,4x3,5x16,6x3" and (
        cover.get("indexed_formula_sha256_aggregate") != data["formula_aggregate_sha256"]
        or formula_aggregate.hexdigest() != data["formula_aggregate_sha256"]
    ):
        raise ViprCertificateError("profile-C indexed formula aggregate mismatch")
    if sum(int(record["orbit_size"]) for record in catalog) != data["raw_states"]:
        raise ViprCertificateError("VIPR orbit sizes do not cover the raw state space")
    release_bytes = _verify_release(release, manifest_path, manifest, data)
    if release.get("certificate_bytes") != certificate_bytes:
        raise ViprCertificateError("VIPR release does not bind every certificate")
    return {
        "status": "VERIFIED",
        "profile": profile,
        "strategy": "scip_vipr_orbit_cover",
        "orbits": data["orbits"],
        "raw_states": data["raw_states"],
        "certificate_bytes": certificate_bytes,
        "release_bytes": release_bytes,
        "checker": "viprchk",
        "vipr_source_commit": VIPR_SOURCE_COMMIT,
    }


def _parse_opb(text: str) -> tuple[int, list[tuple[str, Fraction, tuple[tuple[int, Fraction], ...]]]]:
    lines = text.splitlines()
    match = re.fullmatch(
        r"\* #variable= (\d+) #constraint= (\d+) #equal= (\d+) intsize= (\d+)",
        lines[0],
    )
    if match is None:
        raise ViprCertificateError("malformed generated OPB header")
    variables, declared_constraints = int(match.group(1)), int(match.group(2))
    constraints = []
    for line in lines[1:]:
        if not line or line.startswith("*"):
            continue
        if not line.endswith(";"):
            raise ViprCertificateError("malformed generated OPB constraint")
        body = line[:-1]
        for marker, sense in ((" >= ", "G"), (" <= ", "L"), (" = ", "E")):
            if marker in body:
                left, right = body.rsplit(marker, 1)
                break
        else:
            raise ViprCertificateError("generated OPB constraint lacks a relation")
        tokens = left.split()
        if len(tokens) % 2:
            raise ViprCertificateError("malformed generated OPB coefficient list")
        coefficients = tuple(
            (int(tokens[index + 1][1:]) - 1, Fraction(tokens[index]))
            for index in range(0, len(tokens), 2)
        )
        constraints.append((sense, Fraction(right), coefficients))
    if len(constraints) != declared_constraints:
        raise ViprCertificateError("generated OPB constraint count mismatch")
    return variables, constraints


def _vipr_constraint(line: str) -> tuple[str, Fraction, tuple[tuple[int, Fraction], ...]]:
    tokens = line.split()
    if len(tokens) < 4 or tokens[1] not in {"G", "L", "E"}:
        raise ViprCertificateError("malformed original VIPR constraint")
    sense, right, count = tokens[1], Fraction(tokens[2]), int(tokens[3])
    if len(tokens) != 4 + 2 * count:
        raise ViprCertificateError("malformed original VIPR coefficient list")
    coefficients = tuple(
        (int(tokens[index]), Fraction(tokens[index + 1]))
        for index in range(4, len(tokens), 2)
    )
    return sense, right, coefficients


def verify_vipr_embedded_model(opb_text: str, certificate: TextIO) -> dict[str, int]:
    """Prove that a standalone VIPR certificate embeds the generated OPB model.

    ``viprchk`` checks the derivation from the certificate's ``CON`` section.
    This independent comparison closes the other half of the trust boundary by
    matching that section, coefficient for coefficient, to the regenerated OPB.
    """

    opb_variables, opb_constraints = _parse_opb(opb_text)
    vipr_variables = None
    for line in certificate:
        if line.startswith("VAR "):
            vipr_variables = int(line.split()[1])
        if line.startswith("CON "):
            fields = line.split()
            if len(fields) != 3:
                raise ViprCertificateError("malformed VIPR CON header")
            total, bound_count = int(fields[1]), int(fields[2])
            break
    else:
        raise ViprCertificateError("VIPR certificate lacks a CON section")
    if vipr_variables != opb_variables or total - bound_count != len(opb_constraints):
        raise ViprCertificateError("VIPR model dimensions differ from the generated OPB")
    originals = []
    for index in range(total):
        line = certificate.readline()
        if not line:
            raise ViprCertificateError("truncated VIPR CON section")
        if index < total - bound_count:
            originals.append(_vipr_constraint(line))
    if originals != opb_constraints:
        for index, (observed, expected) in enumerate(
            itertools.zip_longest(originals, opb_constraints)
        ):
            if observed != expected:
                raise ViprCertificateError(
                    f"VIPR original constraint differs from OPB constraint {index}"
                )
        raise ViprCertificateError("VIPR original constraints differ from the OPB")
    relation = certificate.readline().strip()
    if relation != "RTP infeas":
        raise ViprCertificateError("VIPR certificate does not claim infeasibility")
    return {
        "variables": opb_variables,
        "model_constraints": len(opb_constraints),
        "bound_constraints": bound_count,
    }


def verify_compressed_vipr_embedded_model(
    opb_text: str,
    compressed: BinaryIO,
) -> dict[str, int]:
    """Apply :func:`verify_vipr_embedded_model` to one XZ member stream."""

    with lzma.open(compressed, "rt", encoding="ascii") as certificate:
        return verify_vipr_embedded_model(opb_text, certificate)
