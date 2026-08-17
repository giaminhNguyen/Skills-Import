#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser/writer cho file I2Languages.asset (Unity YAML) của I2 Localization.

KHÔNG dùng thư viện YAML: file .asset của Unity phải giữ nguyên format, thứ tự,
comment header (%YAML / %TAG) và các field không liên quan. Ở đây parse theo dòng
và chỉ ghi đè đúng các dòng trong block `Languages:` của từng term.

Cấu trúc block một term trong asset:

    mTerms:
    - Term: remove ads
      TermType: 0
      Description:
      Languages:
      - English value
      - <lang 2>
      ...
      Flags: 000000000000000000000000000000
      Languages_Touch: []

Danh sách ngôn ngữ nằm cuối file:

    mLanguages:
    - Name: English
      Code: en
      Flags: 0
"""

import re

TERM_RE = re.compile(r"^    - Term:(.*)$")
LANG_HEADER = "      Languages:"
LANG_ITEM_RE = re.compile(r"^      -(?: (.*)|)$")
LANGS_HEADER = "    mLanguages:"
LANG_NAME_RE = re.compile(r"^    - Name:(.*)$")
LANG_CODE_RE = re.compile(r"^      Code:(.*)$")

EMPTY_ITEM = "      - "  # Unity ghi kèm 1 space ở cuối cho chuỗi rỗng


# --------------------------------------------------------------------------
# YAML scalar: decode (đọc từ asset) / encode (ghi ra asset)
# --------------------------------------------------------------------------

def _closes_single(body):
    """body = phần sau dấu ' mở đầu. True nếu đã có dấu ' đóng."""
    i = 0
    while i < len(body):
        if body[i] == "'":
            if i + 1 < len(body) and body[i + 1] == "'":
                i += 2
                continue
            return True
        i += 1
    return False


def _closes_double(body):
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            i += 2
            continue
        if c == '"':
            return True
        i += 1
    return False


def _is_complete(raw):
    t = raw.strip()
    if t.startswith("'"):
        return _closes_single(t[1:])
    if t.startswith('"'):
        return _closes_double(t[1:])
    return True


def _fold(segments):
    """Gộp scalar quoted nhiều dòng theo luật YAML: 1 xuống dòng -> space,
    n dòng trống -> n newline."""
    out = segments[0]
    blanks = 0
    for seg in segments[1:]:
        if seg == "":
            blanks += 1
            continue
        out += ("\n" * blanks) if blanks else " "
        out += seg
        blanks = 0
    return out


def _unescape_double(s):
    out = []
    i = 0
    mapping = {"n": "\n", "t": "\t", "r": "\r", "0": "\0",
               "\\": "\\", '"': '"', "/": "/", "'": "'"}
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            if nxt in ("x", "u", "U"):
                width = {"x": 2, "u": 4, "U": 8}[nxt]
                hexs = s[i + 2:i + 2 + width]
                try:
                    out.append(chr(int(hexs, 16)))
                    i += 2 + width
                    continue
                except ValueError:
                    pass
        out.append(c)
        i += 1
    return "".join(out)


def decode_scalar(raw):
    t = raw.strip()
    if t == "":
        return ""
    if len(t) >= 2 and t.startswith("'") and t.endswith("'"):
        return t[1:-1].replace("''", "'")
    if len(t) >= 2 and t.startswith('"') and t.endswith('"'):
        return _unescape_double(t[1:-1])
    return t


def read_scalar(lines, idx, raw_value):
    """Đọc 1 scalar có thể trải nhiều dòng. Trả (value, last_line_index)."""
    segments = [raw_value.strip()]
    buf = raw_value
    while not _is_complete(buf) and idx + 1 < len(lines):
        idx += 1
        segments.append(lines[idx].strip())
        buf += "\n" + lines[idx]
    if len(segments) > 1:
        return decode_scalar(_fold(segments)), idx
    return decode_scalar(segments[0]), idx


_PLAIN_UNSAFE_START = set("-?:,[]{}#&*!|>'\"%@`")
_YAML_KEYWORDS = {
    "true", "false", "null", "yes", "no", "on", "off", "y", "n", "~",
    "True", "False", "Null", "Yes", "No", "On", "Off", "TRUE", "FALSE", "NULL",
}
_NUMERIC_RE = re.compile(r"^[-+]?(\d[\d_]*(\.\d*)?([eE][-+]?\d+)?|\.\d+|0[xXbBoO][0-9a-fA-F_]+)$")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def _is_plain_safe(s):
    if s == "" or s != s.strip():
        return False
    if s[0] in _PLAIN_UNSAFE_START:
        return False
    if s in _YAML_KEYWORDS or _NUMERIC_RE.match(s):
        return False
    if ": " in s or s.endswith(":") or " #" in s:
        return False
    if "\n" in s or "\r" in s or "\t" in s:
        return False
    return True


def encode_scalar(s):
    """Chuỗi -> scalar YAML an toàn cho Unity đọc lại."""
    if s == "":
        return ""
    if "\n" in s or "\r" in s or "\t" in s or _CONTROL_RE.search(s):
        esc = (s.replace("\\", "\\\\").replace('"', '\\"')
                .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))
        return '"' + esc + '"'
    if _is_plain_safe(s):
        return s
    return "'" + s.replace("'", "''") + "'"


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------

class Term(object):
    def __init__(self, name, term_line, lang_start, lang_end, values):
        self.name = name            # tên term đã decode
        self.term_line = term_line  # index dòng "- Term: ..."
        self.lang_start = lang_start  # index dòng đầu của list Languages
        self.lang_end = lang_end      # index sau dòng cuối (exclusive)
        self.values = values          # list[str] theo thứ tự ngôn ngữ


class I2Asset(object):
    def __init__(self, path, lines, terms, languages):
        self.path = path
        self.lines = lines
        self.terms = terms                 # list[Term]
        self.languages = languages         # list[(name, code)]

    # -- truy vấn ---------------------------------------------------------

    @property
    def codes(self):
        return [c for _, c in self.languages]

    def index_of(self, code):
        for i, (_, c) in enumerate(self.languages):
            if c == code:
                return i
        for i, (name, _) in enumerate(self.languages):
            if name == code:
                return i
        return -1

    def term_map(self):
        return {t.name: t for t in self.terms}

    # -- ghi --------------------------------------------------------------

    def set_value(self, term, code, value):
        i = self.index_of(code)
        if i < 0:
            raise KeyError("Không có ngôn ngữ '%s' trong asset" % code)
        while len(term.values) <= i:
            term.values.append("")
        term.values[i] = value

    def save(self, path=None):
        out = list(self.lines)
        # thay từ dưới lên để index dòng phía trên không bị lệch
        for term in sorted(self.terms, key=lambda t: t.lang_start, reverse=True):
            vals = list(term.values)
            while len(vals) < len(self.languages):
                vals.append("")
            block = []
            for v in vals:
                enc = encode_scalar(v)
                block.append(EMPTY_ITEM if enc == "" else "      - " + enc)
            out[term.lang_start:term.lang_end] = block
        text = "\n".join(out)
        with open(path or self.path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


# --------------------------------------------------------------------------
# Parse
# --------------------------------------------------------------------------

def load(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        raw = f.read()
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    terms = []
    languages = []
    i = 0
    n = len(lines)
    in_langs = False

    while i < n:
        line = lines[i]

        if line == LANGS_HEADER:
            in_langs = True
            i += 1
            continue

        if in_langs:
            m = LANG_NAME_RE.match(line)
            if m:
                name, i = read_scalar(lines, i, m.group(1))
                code = ""
                j = i + 1
                while j < n:
                    mc = LANG_CODE_RE.match(lines[j])
                    if mc:
                        code, j = read_scalar(lines, j, mc.group(1))
                        break
                    if LANG_NAME_RE.match(lines[j]) or not lines[j].startswith("      "):
                        break
                    j += 1
                languages.append((name, code))
                i += 1
                continue
            if line and not line.startswith("    "):
                in_langs = False
            elif line.startswith("    ") and not line.startswith("    - ") and not line.startswith("      "):
                in_langs = False
            i += 1
            continue

        m = TERM_RE.match(line)
        if m:
            term_line = i
            name, i = read_scalar(lines, i, m.group(1))
            # tìm header Languages: trong block term này
            j = i + 1
            lang_start = lang_end = -1
            values = []
            while j < n:
                if lines[j] == LANG_HEADER:
                    j += 1
                    lang_start = j
                    while j < n:
                        mi = LANG_ITEM_RE.match(lines[j])
                        if not mi:
                            break
                        val, j = read_scalar(lines, j, mi.group(1) or "")
                        values.append(val)
                        j += 1
                    lang_end = j
                    break
                if TERM_RE.match(lines[j]) or lines[j] == LANGS_HEADER:
                    break
                j += 1
            if lang_start >= 0:
                terms.append(Term(name, term_line, lang_start, lang_end, values))
                i = lang_end
                continue
        i += 1

    if not languages:
        raise RuntimeError("Không tìm thấy block mLanguages trong %s" % path)

    return I2Asset(path, lines, terms, languages)
