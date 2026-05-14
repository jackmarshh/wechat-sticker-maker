#!/bin/bash
# Build wechat-sticker-maker.skill (ZIP package)
set -e

OUTPUT="wechat-sticker-maker.skill"

echo "Building $OUTPUT..."

zip -r "$OUTPUT" \
  SKILL.md \
  references/ \
  scripts/ \
  templates/ \
  --exclude "*.pyc" \
  --exclude "__pycache__/*" \
  --exclude ".DS_Store"

echo "✓ Built: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
