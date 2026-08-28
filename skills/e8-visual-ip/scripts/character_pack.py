#!/usr/bin/env python3
"""创建、更新、校验和解析可移植的 E8 视觉 IP 角色包。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


SCRIPT_INTERFACE = "cli"
SCHEMA_VERSION = "1.0"
KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def timestamp_slug() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")


def read_utf8(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"文本文件不得包含 UTF-8 BOM：{path}")
    return raw.decode("utf-8")


def read_non_empty_utf8(path: Path, label: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"{label} 不存在：{path}")
    text = read_utf8(path)
    if not text.strip():
        raise ValueError(f"{label} 不能为空：{path}")
    return text


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_utf8(path))
    if not isinstance(value, dict):
        raise TypeError(f"JSON 顶层必须是对象：{path}")
    return value


def json_text(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    write_text_atomic(path, json_text(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_key(value: str, label: str) -> str:
    if not KEY_PATTERN.fullmatch(value):
        raise ValueError(f"{label} 只能包含小写字母、数字和连字符：{value}")
    return value


def require_display_name(value: str, label: str) -> str:
    if not value.strip():
        raise ValueError(f"{label} 不能为空。")
    return value.strip()


def resolve_source_image(workspace_root: Path, value: Path, label: str) -> Path:
    source = value if value.is_absolute() else workspace_root / value
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"{label} 不存在：{source}")
    if source.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"{label} 格式不支持：{source}")
    return source


def visual_ip_root(workspace_root: Path) -> Path:
    return workspace_root.resolve() / ".creator-space" / "visual-ip"


def characters_root(workspace_root: Path) -> Path:
    return visual_ip_root(workspace_root) / "characters"


def character_directory(workspace_root: Path, key: str) -> Path:
    return characters_root(workspace_root) / require_key(key, "character key")


def relative_to_character(character_dir: Path, path: Path) -> str:
    return path.resolve().relative_to(character_dir.resolve()).as_posix()


def resolve_character_file(character_dir: Path, value: str, label: str) -> Path:
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError(f"{label} 必须是角色包相对路径：{value}")
    resolved = (character_dir / relative).resolve()
    if character_dir.resolve() not in resolved.parents:
        raise ValueError(f"{label} 逃逸出角色包：{value}")
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} 文件不存在：{resolved}")
    return resolved


def copy_file_non_destructive(source: Path, destination: Path) -> None:
    if destination.exists():
        raise FileExistsError(f"目标文件已存在，拒绝覆盖：{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)


def copy_text_non_destructive(text: str, destination: Path) -> None:
    if destination.exists():
        raise FileExistsError(f"目标文件已存在，拒绝覆盖：{destination}")
    write_text_atomic(destination, text)


def manifest_path(character_dir: Path) -> Path:
    return character_dir / "manifest.json"


def load_manifest(character_dir: Path) -> dict[str, Any]:
    return load_json(manifest_path(character_dir))


def style_entry(
    character_dir: Path,
    style_id: str,
    style_name: str,
    reference_path: Path,
    definition_path: Path,
    timestamp: str,
) -> dict[str, Any]:
    return {
        "style_id": require_key(style_id, "style id"),
        "display_name": require_display_name(style_name, "style name"),
        "reference": relative_to_character(character_dir, reference_path),
        "reference_sha256": sha256_file(reference_path),
        "definition": relative_to_character(character_dir, definition_path),
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def validate_style_entry(
    character_dir: Path,
    style: dict[str, Any],
    label: str,
) -> None:
    expected = {
        "style_id",
        "display_name",
        "reference",
        "reference_sha256",
        "definition",
        "created_at",
        "updated_at",
    }
    if set(style) != expected:
        raise ValueError(f"{label} 字段非法。")
    require_key(style["style_id"], f"{label}.style_id")
    require_display_name(style["display_name"], f"{label}.display_name")
    reference = resolve_character_file(character_dir, style["reference"], f"{label}.reference")
    if reference.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"{label}.reference 不是支持的图片：{reference}")
    if sha256_file(reference) != style["reference_sha256"]:
        raise ValueError(f"{label}.reference_sha256 与图片不一致。")
    definition = resolve_character_file(character_dir, style["definition"], f"{label}.definition")
    read_non_empty_utf8(definition, f"{label}.definition")


def validate_character(character_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(character_dir)
    expected = {
        "schema_version",
        "character_key",
        "display_name",
        "created_at",
        "updated_at",
        "identity",
        "styles",
    }
    if set(manifest) != expected:
        raise ValueError(f"manifest.json 字段非法：{character_dir}")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("manifest.schema_version 不支持。")
    if manifest["character_key"] != character_dir.name:
        raise ValueError("manifest.character_key 必须等于目录名称。")
    require_key(manifest["character_key"], "manifest.character_key")
    require_display_name(manifest["display_name"], "manifest.display_name")

    identity = manifest["identity"]
    if not isinstance(identity, dict) or set(identity) != {
        "reference",
        "reference_sha256",
        "definition",
    }:
        raise ValueError("manifest.identity 字段非法。")
    reference = resolve_character_file(character_dir, identity["reference"], "identity.reference")
    if reference.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError("identity.reference 不是支持的图片。")
    if sha256_file(reference) != identity["reference_sha256"]:
        raise ValueError("identity.reference_sha256 与图片不一致。")
    definition = resolve_character_file(character_dir, identity["definition"], "identity.definition")
    read_non_empty_utf8(definition, "identity.definition")

    styles = manifest["styles"]
    if not isinstance(styles, list) or not styles:
        raise ValueError("正式角色包至少需要一个已确认风格。")
    style_ids = [style["style_id"] for style in styles]
    if len(style_ids) != len(set(style_ids)):
        raise ValueError("角色包存在重复 style_id。")
    for index, style in enumerate(styles):
        validate_style_entry(character_dir, style, f"styles[{index}]")

    allowed_files = {"manifest.json", "character.md"}
    actual_files = {item.name for item in character_dir.iterdir() if item.is_file()}
    allowed_dirs = {"refs", "styles"}
    actual_dirs = {item.name for item in character_dir.iterdir() if item.is_dir()}
    if actual_files != allowed_files or actual_dirs != allowed_dirs:
        raise ValueError(
            f"角色包结构非法：文件={sorted(actual_files)}，目录={sorted(actual_dirs)}"
        )
    return manifest


def backup_character(workspace_root: Path, key: str) -> Path:
    source = character_directory(workspace_root, key)
    destination = visual_ip_root(workspace_root) / "backups" / key / timestamp_slug()
    if destination.exists():
        raise FileExistsError(f"备份目录已存在：{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return destination


def save_character(
    workspace_root: Path,
    key: str,
    display_name: str,
    identity_image: Path,
    character_definition: Path,
    style_id: str,
    style_name: str,
    style_definition: Path,
) -> dict[str, Any]:
    character_dir = character_directory(workspace_root, key)
    if character_dir.exists():
        raise FileExistsError(f"角色已经存在，请使用 update-character：{character_dir}")
    source_image = resolve_source_image(workspace_root, identity_image, "正式人物图")
    character_text = read_non_empty_utf8(character_definition.resolve(), "人物定义")
    style_text = read_non_empty_utf8(style_definition.resolve(), "风格定义")
    timestamp = now_iso()

    identity_target = character_dir / "refs" / f"identity{source_image.suffix.lower()}"
    style_dir = character_dir / "styles" / require_key(style_id, "style id")
    style_reference = style_dir / f"reference{source_image.suffix.lower()}"
    style_definition_target = style_dir / "style.md"
    character_dir.mkdir(parents=True)
    copy_file_non_destructive(source_image, identity_target)
    copy_text_non_destructive(character_text, character_dir / "character.md")
    copy_file_non_destructive(source_image, style_reference)
    copy_text_non_destructive(style_text, style_definition_target)

    style = style_entry(
        character_dir,
        style_id,
        style_name,
        style_reference,
        style_definition_target,
        timestamp,
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "character_key": require_key(key, "character key"),
        "display_name": require_display_name(display_name, "display name"),
        "created_at": timestamp,
        "updated_at": timestamp,
        "identity": {
            "reference": relative_to_character(character_dir, identity_target),
            "reference_sha256": sha256_file(identity_target),
            "definition": "character.md",
        },
        "styles": [style],
    }
    write_json_atomic(manifest_path(character_dir), manifest)
    validate_character(character_dir)
    return {
        "action": "character_saved",
        "character_key": key,
        "display_name": manifest["display_name"],
        "style_id": style_id,
        "character_dir": str(character_dir),
    }


def add_style(
    workspace_root: Path,
    key: str,
    style_id: str,
    style_name: str,
    style_image: Path,
    style_definition: Path,
) -> dict[str, Any]:
    character_dir = character_directory(workspace_root, key)
    manifest = validate_character(character_dir)
    if style_id in {item["style_id"] for item in manifest["styles"]}:
        raise FileExistsError(f"风格已经存在，请使用 update-style：{style_id}")
    source_image = resolve_source_image(workspace_root, style_image, "正式风格图")
    style_text = read_non_empty_utf8(style_definition.resolve(), "风格定义")
    style_dir = character_dir / "styles" / require_key(style_id, "style id")
    reference_target = style_dir / f"reference{source_image.suffix.lower()}"
    definition_target = style_dir / "style.md"
    copy_file_non_destructive(source_image, reference_target)
    copy_text_non_destructive(style_text, definition_target)
    timestamp = now_iso()
    manifest["styles"].append(
        style_entry(
            character_dir,
            style_id,
            style_name,
            reference_target,
            definition_target,
            timestamp,
        )
    )
    manifest["styles"] = sorted(manifest["styles"], key=lambda item: item["style_id"])
    manifest["updated_at"] = timestamp
    write_json_atomic(manifest_path(character_dir), manifest)
    validate_character(character_dir)
    return {
        "action": "style_added",
        "character_key": key,
        "style_id": style_id,
        "character_dir": str(character_dir),
    }


def update_character(
    workspace_root: Path,
    key: str,
    display_name: str,
    identity_image: Path,
    character_definition: Path,
    style_id: str,
    style_name: str,
    style_definition: Path,
) -> dict[str, Any]:
    character_dir = character_directory(workspace_root, key)
    validate_character(character_dir)
    backup = backup_character(workspace_root, key)
    temporary_key = f"{key}-replacement-{uuid4().hex[:8]}"
    replacement = save_character(
        workspace_root,
        temporary_key,
        display_name,
        identity_image,
        character_definition,
        style_id,
        style_name,
        style_definition,
    )
    replacement_dir = Path(replacement["character_dir"])
    retired_dir = characters_root(workspace_root) / f".{key}.retired-{uuid4().hex[:8]}"
    os.replace(character_dir, retired_dir)
    os.replace(replacement_dir, character_dir)
    shutil.rmtree(retired_dir)
    manifest = load_manifest(character_dir)
    manifest["character_key"] = key
    manifest["updated_at"] = now_iso()
    write_json_atomic(manifest_path(character_dir), manifest)
    validate_character(character_dir)
    return {
        "action": "character_updated",
        "character_key": key,
        "character_dir": str(character_dir),
        "backup_dir": str(backup),
    }


def update_style(
    workspace_root: Path,
    key: str,
    style_id: str,
    style_name: str,
    style_image: Path,
    style_definition: Path,
) -> dict[str, Any]:
    character_dir = character_directory(workspace_root, key)
    manifest = validate_character(character_dir)
    matches = [item for item in manifest["styles"] if item["style_id"] == style_id]
    if len(matches) != 1:
        raise ValueError(f"找不到唯一正式风格：{style_id}")
    backup = backup_character(workspace_root, key)
    style_dir = character_dir / "styles" / style_id
    source_image = resolve_source_image(workspace_root, style_image, "正式风格图")
    style_text = read_non_empty_utf8(style_definition.resolve(), "风格定义")
    replacement_dir = character_dir / "styles" / f".{style_id}.replacement-{uuid4().hex[:8]}"
    replacement_reference = replacement_dir / f"reference{source_image.suffix.lower()}"
    replacement_definition = replacement_dir / "style.md"
    copy_file_non_destructive(source_image, replacement_reference)
    copy_text_non_destructive(style_text, replacement_definition)
    retired_dir = character_dir / "styles" / f".{style_id}.retired-{uuid4().hex[:8]}"
    os.replace(style_dir, retired_dir)
    os.replace(replacement_dir, style_dir)
    shutil.rmtree(retired_dir)
    reference_target = style_dir / f"reference{source_image.suffix.lower()}"
    definition_target = style_dir / "style.md"
    timestamp = now_iso()
    replacement = style_entry(
        character_dir,
        style_id,
        style_name,
        reference_target,
        definition_target,
        matches[0]["created_at"],
    )
    replacement["updated_at"] = timestamp
    manifest["styles"] = [
        replacement if item["style_id"] == style_id else item
        for item in manifest["styles"]
    ]
    manifest["updated_at"] = timestamp
    write_json_atomic(manifest_path(character_dir), manifest)
    validate_character(character_dir)
    return {
        "action": "style_updated",
        "character_key": key,
        "style_id": style_id,
        "character_dir": str(character_dir),
        "backup_dir": str(backup),
    }


def list_characters(workspace_root: Path) -> dict[str, Any]:
    root = characters_root(workspace_root)
    characters = []
    if root.is_dir():
        for directory in sorted(item for item in root.iterdir() if item.is_dir()):
            manifest = validate_character(directory)
            characters.append({
                "character_key": manifest["character_key"],
                "display_name": manifest["display_name"],
                "styles": [
                    {
                        "style_id": style["style_id"],
                        "display_name": style["display_name"],
                    }
                    for style in manifest["styles"]
                ],
                "character_dir": str(directory),
            })
    return {"characters": characters, "count": len(characters)}


def resolve_character(workspace_root: Path, key: str, style_id: str | None) -> dict[str, Any]:
    character_dir = character_directory(workspace_root, key)
    manifest = validate_character(character_dir)
    result: dict[str, Any] = {
        "character_key": key,
        "display_name": manifest["display_name"],
        "character_definition": str(
            resolve_character_file(character_dir, manifest["identity"]["definition"], "人物定义")
        ),
        "identity_reference": str(
            resolve_character_file(character_dir, manifest["identity"]["reference"], "身份锚点")
        ),
        "available_styles": [
            {"style_id": item["style_id"], "display_name": item["display_name"]}
            for item in manifest["styles"]
        ],
    }
    if style_id is not None:
        matches = [item for item in manifest["styles"] if item["style_id"] == style_id]
        if len(matches) != 1:
            raise ValueError(f"找不到唯一正式风格：{style_id}")
        style = matches[0]
        result["style"] = {
            "style_id": style["style_id"],
            "display_name": style["display_name"],
            "definition": str(
                resolve_character_file(character_dir, style["definition"], "风格定义")
            ),
            "reference": str(
                resolve_character_file(character_dir, style["reference"], "风格锚点")
            ),
        }
    return result


def validate_workspace(workspace_root: Path) -> dict[str, Any]:
    listing = list_characters(workspace_root)
    return {
        "valid": True,
        "character_count": listing["count"],
        "style_count": sum(len(item["styles"]) for item in listing["characters"]),
        "root": str(visual_ip_root(workspace_root)),
    }


def add_common_character_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--key", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--identity-image", required=True, type=Path)
    parser.add_argument("--character-definition", required=True, type=Path)
    parser.add_argument("--style-id", required=True)
    parser.add_argument("--style-name", required=True)
    parser.add_argument("--style-definition", required=True, type=Path)


def add_common_style_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--key", required=True)
    parser.add_argument("--style-id", required=True)
    parser.add_argument("--style-name", required=True)
    parser.add_argument("--style-image", required=True, type=Path)
    parser.add_argument("--style-definition", required=True, type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="管理可移植 E8 视觉 IP 角色包。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save = subparsers.add_parser("save-character", help="保存首次确认的人物和初始风格。")
    add_common_character_args(save)

    update = subparsers.add_parser("update-character", help="备份后更新人物核心身份。")
    add_common_character_args(update)

    add = subparsers.add_parser("add-style", help="为人物增加正式确认风格。")
    add_common_style_args(add)

    update_style_parser = subparsers.add_parser("update-style", help="备份后更新正式风格。")
    add_common_style_args(update_style_parser)

    listing = subparsers.add_parser("list", help="列出当前工作区可复用人物。")
    listing.add_argument("--workspace-root", required=True, type=Path)

    resolve = subparsers.add_parser("resolve", help="解析人物和可选风格参考。")
    resolve.add_argument("--workspace-root", required=True, type=Path)
    resolve.add_argument("--key", required=True)
    resolve.add_argument("--style-id")

    validate = subparsers.add_parser("validate", help="校验全部角色包。")
    validate.add_argument("--workspace-root", required=True, type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    workspace_root = args.workspace_root.resolve()
    if not workspace_root.is_dir():
        raise NotADirectoryError(f"工作区根目录不存在：{workspace_root}")

    if args.command == "save-character":
        result = save_character(
            workspace_root,
            args.key,
            args.display_name,
            args.identity_image,
            args.character_definition,
            args.style_id,
            args.style_name,
            args.style_definition,
        )
    elif args.command == "update-character":
        result = update_character(
            workspace_root,
            args.key,
            args.display_name,
            args.identity_image,
            args.character_definition,
            args.style_id,
            args.style_name,
            args.style_definition,
        )
    elif args.command == "add-style":
        result = add_style(
            workspace_root,
            args.key,
            args.style_id,
            args.style_name,
            args.style_image,
            args.style_definition,
        )
    elif args.command == "update-style":
        result = update_style(
            workspace_root,
            args.key,
            args.style_id,
            args.style_name,
            args.style_image,
            args.style_definition,
        )
    elif args.command == "list":
        result = list_characters(workspace_root)
    elif args.command == "resolve":
        result = resolve_character(workspace_root, args.key, args.style_id)
    elif args.command == "validate":
        result = validate_workspace(workspace_root)
    else:
        raise AssertionError(f"未处理的命令：{args.command}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
