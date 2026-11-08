# libsast

Generic SAST for Security Engineers. Powered by [tree-sitter](https://tree-sitter.github.io/tree-sitter/) AST pattern matcher, regex based pattern matcher, and semantic aware [semgrep](https://github.com/returntocorp/semgrep).

Made with ![Love](https://cloud.githubusercontent.com/assets/4301109/16754758/82e3a63c-4813-11e6-9430-6015d98aeaab.png) in India [![Tweet](https://img.shields.io/twitter/url?url=https://github.com/ajinabraham/libsast)](https://twitter.com/intent/tweet/?text=Generic%20SAST%20for%20Security%20Engineers.%20Powered%20by%20regex%20based%20pattern%20matcher%20and%20semantic%20aware%20semgrep%20by%20%40ajinabraham%20%40OpenSecurity_IN&url=https://github.com/ajinabraham/libsast)

[![PyPI version](https://badge.fury.io/py/libsast.svg)](https://badge.fury.io/py/libsast)
[![platform](https://img.shields.io/badge/platform-windows%2Fosx%2Flinux-green.svg)](https://github.com/ajinabraham/libsast)
[![License](https://img.shields.io/:license-lgpl3+-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Build](https://github.com/ajinabraham/libsast/workflows/Build/badge.svg)](https://github.com/ajinabraham/libsast/actions?query=workflow%3ABuild)

### Support libsast

* **Donate via Paypal:** [![Donate via Paypal](https://user-images.githubusercontent.com/4301109/76471686-c43b0500-63c9-11ea-8225-2a305efb3d87.gif)](https://paypal.me/ajinabraham)
* **Sponsor the Project:** [![Github Sponsors](https://user-images.githubusercontent.com/4301109/95517226-9e410780-098e-11eb-9ef5-7b8c7561d725.png)](https://github.com/sponsors/ajinabraham)

## Install

```bash
pip install libsast
# Optional Tree-sitter language grammar extras:
pip install "libsast[treesitter]"  # 165+ languages via tree-sitter-language-pack
pip install "libsast[mobile]"      # JS, TS/TSX, Java, Kotlin, Swift, ObjC, C#
pip install "libsast[js]"          # JavaScript and TypeScript/TSX
# Or install any individual tree-sitter-<lang> package alongside libsast:
pip install libsast tree-sitter-python
# Optional Semgrep support (macOS/Linux):
pip install semgrep==1.172.0
```

Pattern Matcher and Tree-sitter Matcher are cross-platform (Windows, macOS, and Linux). Semgrep supports macOS and Linux.

## Command Line Options

```bash
$ libsast
usage: libsast [-h] [-o OUTPUT] [-p PATTERN_FILE] [-t TS_PATTERN_FILE]
               [-s SGREP_PATTERN_FILE]
               [--ts-file-extensions TS_FILE_EXTENSIONS [TS_FILE_EXTENSIONS ...]]
               [--sgrep-file-extensions SGREP_FILE_EXTENSIONS [SGREP_FILE_EXTENSIONS ...]]
               [--file-extensions FILE_EXTENSIONS [FILE_EXTENSIONS ...]]
               [--ignore-filenames IGNORE_FILENAMES [IGNORE_FILENAMES ...]]
               [--ignore-extensions IGNORE_EXTENSIONS [IGNORE_EXTENSIONS ...]]
               [--ignore-paths IGNORE_PATHS [IGNORE_PATHS ...]]
               [--show-progress] [--cpu-core CPU_CORE] [-v]
               [path ...]

positional arguments:
  path                  Path can be file(s) or directories

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output filename to save JSON report.
  -p PATTERN_FILE, --pattern-file PATTERN_FILE
                        YAML pattern file, directory or url
  -t TS_PATTERN_FILE, --ts-pattern-file TS_PATTERN_FILE
                        Tree-sitter YAML pattern file, directory or url
  -s SGREP_PATTERN_FILE, --sgrep-pattern-file SGREP_PATTERN_FILE
                        sgrep rules directory
  --ts-file-extensions TS_FILE_EXTENSIONS [TS_FILE_EXTENSIONS ...]
                        File extensions that should be scanned with
                        tree-sitter matcher
  --sgrep-file-extensions SGREP_FILE_EXTENSIONS [SGREP_FILE_EXTENSIONS ...]
                        File extensions that should be scanned with semantic
                        grep
  --file-extensions FILE_EXTENSIONS [FILE_EXTENSIONS ...]
                        File extensions that should be scanned with pattern
                        matcher
  --ignore-filenames IGNORE_FILENAMES [IGNORE_FILENAMES ...]
                        File name(s) to ignore
  --ignore-extensions IGNORE_EXTENSIONS [IGNORE_EXTENSIONS ...]
                        File extension(s) to ignore in lower case
  --ignore-paths IGNORE_PATHS [IGNORE_PATHS ...]
                        Path(s) to ignore
  --show-progress       Show scan progress
  --cpu-core CPU_CORE   No of CPU cores to use. Use all cores by default
  -v, --version         Show libsast version
```


## Example Usage

```json
$ libsast -s tests/assets/rules/semantic_grep/ -p tests/assets/rules/pattern_matcher/ tests/assets/files/
{
  "pattern_matcher": {
    "test_regex": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            28,
            28
          ],
          "match_position": [
            1141,
            1149
          ],
          "match_string": ".close()"
        }
      ],
      "metadata": {}
    },
    "test_regex_and": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            3,
            3
          ],
          "match_position": [
            52,
            66
          ],
          "match_string": "webkit.WebView"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            7,
            7
          ],
          "match_position": [
            194,
            254
          ],
          "match_string": ".loadUrl(\"file:/\" + Environment.getExternalStorageDirectory("
        }
      ],
      "metadata": {}
    },
    "test_regex_and_not": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            42,
            42
          ],
          "match_position": [
            1415,
            1424
          ],
          "match_string": "WKWebView"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            40,
            40
          ],
          "match_position": [
            1363,
            1372
          ],
          "match_string": "WKWebView"
        }
      ],
      "metadata": {}
    },
    "test_regex_and_or": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            50,
            50
          ],
          "match_position": [
            1551,
            1571
          ],
          "match_string": "telephony.SmsManager"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            58,
            58
          ],
          "match_position": [
            1973,
            1988
          ],
          "match_string": "sendTextMessage"
        }
      ],
      "metadata": {}
    },
    "test_regex_multiline_and_metadata": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            52,
            52
          ],
          "match_position": [
            1586,
            1684
          ],
          "match_string": "public void onRequestPermissionsResult(int requestCode,String permissions[], int[] grantResults) {"
        },
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            10,
            11
          ],
          "match_position": [
            297,
            368
          ],
          "match_string": "public static ForgeAccount add(Context context, ForgeAccount account) {"
        }
      ],
      "metadata": {
        "cwe": "CWE-1051 Initialization with Hard-Coded Network Resource Configuration Data",
        "description": "This is a rule to test regex",
        "foo": "bar",
        "masvs": "MSTG-STORAGE-3",
        "owasp-mobile": "M1: Improper Platform Usage",
        "owasp-web": "A10: Insufficient Logging & Monitoring",
        "severity": "info"
      }
    },
    "test_regex_or": {
      "files": [
        {
          "file_path": "tests/assets/files/test_matcher.test",
          "match_lines": [
            26,
            26
          ],
          "match_position": [
            1040,
            1067
          ],
          "match_string": "Context.MODE_WORLD_READABLE"
        }
      ],
      "metadata": {}
    }
  },
  "semantic_grep": {
    "errors": [
      {
        "code": 3,
        "level": "warn",
        "message": "Semgrep Core WARN - Lexical error in file tests/assets/files/test_matcher.test:40\n\tunrecognized symbols: !",
        "path": "tests/assets/files/test_matcher.test",
        "type": "Lexical error"
      },
    ],
    "matches": {
      "boto-client-ip": {
        "files": [
          {
            "file_path": "tests/assets/files/example_file.py",
            "match_lines": [
              4,
              4
            ],
            "match_position": [
              24,
              31
            ],
            "match_string": "c = boto3.client(host='8.8.8.8')"
          }
        ],
        "metadata": {
          "cwe": "CWE-1050 Excessive Platform Resource Consumption within a Loop",
          "description": "boto client using IP address",
          "owasp-web": "A8: Insecure Deserialization",
          "severity": "ERROR"
        }
      }
    }
  }
}
```

## Python API

```python
>>> from libsast import Scanner
>>> options = {'match_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/pattern_matcher', 'sgrep_rules': '/Users/ajinabraham/Code/njsscan/njsscan/rules/semantic_grep', 'sgrep_extensions': {'', '.js'}, 'match_extensions': {'.hbs', '.sh', '.ejs', '.toml', '.mustache', '.tmpl', '.jade', '.json', '.ect', '.vue', '.yml', '.hdbs', '.tl', '.html', '.haml', '.dust', '.pug', '.tpl'}, 'ignore_filenames': {'bootstrap.min.js', '.DS_Store', 'bootstrap-tour.js', 'd3.min.js', 'tinymce.js', 'codemirror.js', 'tinymce.min.js', 'react-dom.production.min.js', 'react.js', 'jquery.min.js', 'react.production.min.js', 'codemirror-compressed.js', 'axios.min.js', 'angular.min.js', 'raphael-min.js', 'vue.min.js'}, 'ignore_paths': {'__MACOSX', 'jquery', 'fixtures', 'node_modules', 'bower_components', 'example', 'spec'}, 'show_progress': False}
>>> paths = ['../njsscan/tests/assets/dot_njsscan/']
>>> scanner = Scanner(options, paths)
>>> scanner.scan()
```

## Write your own Static Analysis tool

With libsast, you can write your own static analysis tools. libsast provides three matching engines:

1. **Pattern Matcher (Regex)**
2. **Tree-sitter Matcher (AST)**
3. **Semantic Grep (Semgrep)**

### Pattern Matcher

Pattern Matcher supports any language.

Use [Regex 101](https://regex101.com/r/nGbAay/1) to write simple Python Regex rule patterns.

A sample rule looks like

```yaml
- id: test_regex_or
  message: This is a rule to test regex_or
  input_case: exact
  pattern:
  - MODE_WORLD_READABLE|Context\.MODE_WORLD_READABLE
  - openFileOutput\(\s*".+"\s*,\s*1\s*\)
  severity: error
  type: RegexOr
  metadata:
    owasp-web: a1
    reference: http://foo.bar
    foo: Some extra metadata
```
A rule consists of

* `id` : A unique id for the rule.
* `message`: A description for the rule.
* `input_case`: It can be `exact`, `upper` or `lower`. Data will be converted to lower case/upper case/as it is before comparing with the regex.
* `pattern`: List of patterns depends on `type`.
* `severity`: It can be `error`, `warning` or `info`.
* `type`: Pattern Matcher supports `Regex`, `RegexAnd`, `RegexOr`, `RegexAndOr`, `RegexAndNot` (as well as `TreeSitter`, `TreeSitterAnd`, `TreeSitterOr`, `TreeSitterAndOr`, `TreeSitterAndNot`).
* `metadata` (optional): Define your own custom fields that you can use as metadata along with standard mappings.

```bash
1. Regex - if regex1 in input
2. RegexAnd - if regex1 in input and regex2 in input
3. RegexOr - if regex1 in input or regex2 in input
4. RegexAndOr -  if regex1 in input and (regex2 in input or regex3 in input)
5. RegexAndNot - if regex1 in input and not regex2 in input
```
Example: [Pattern Matcher Rule](https://github.com/ajinabraham/libsast/blob/master/tests/assets/rules/pattern_matcher/patterns.yaml)

Test your pattern matcher rules

`$ libsast -p tests/assets/rules/pattern_matcher/patterns.yaml tests/assets/files/`

### Tree-sitter Matcher

Tree-sitter Matcher provides language-agnostic, syntax-aware AST pattern matching across any language supported by [Tree-sitter](https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html) (JavaScript, TypeScript/TSX, HTML/Vue `<script>`, Java, Kotlin, Swift, Objective-C, Dart, C#, Python, Go, Rust, C/C++, etc.).

Tree-sitter rules can be placed inside `--pattern-file` (`match_rules`) alongside Regex rules or passed separately via `-t` / `ts_rules`:

```yaml
- id: rn_webview_universal_file_access
  type: TreeSitter
  languages: [javascript, typescript, tsx]
  message: WebView allows universal access from file URLs
  severity: error
  pattern: |
    (jsx_opening_element
      name: (_) @_tag (#match? @_tag "WebView$")
      attribute: (jsx_attribute
        (property_identifier) @_prop (#eq? @_prop "allowUniversalAccessFromFileURLs")
        (_ (true)))) @match
  exclude_ancestor: |
    (if_statement condition: (_) @_c (#match? @_c "__DEV__"))
  metadata:
    cwe: cwe-200
    owasp-mobile: m1
    masvs: platform-2
```

Supported rule keys:

* `type`: `TreeSitter`, `TreeSitterAnd`, `TreeSitterOr`, `TreeSitterAndOr`, `TreeSitterAndNot`.
* `pattern`: Tree-sitter S-expression query (or list of queries) capturing `@match`.
* `languages` (optional): List of Tree-sitter language names the rule applies to.
* `exclude_ancestor` (optional): S-expression query; suppresses matches nested inside a matching ancestor node (e.g., `if (__DEV__)`).
* `within_ancestor` (optional): S-expression query; requires `@match` to be nested inside a matching ancestor node.
* `not_within_node` (optional): S-expression query; suppresses `@match` if the matched node itself contains a sub-node matching this query (e.g., missing-property checks).

#### Inbuilt Standard Mapping Support

Metadata fields also support [libsast standard mapping](https://github.com/ajinabraham/libsast/tree/master/libsast/standards).

For example, the metadata field `owasp-web: a1` will get expanded at runtime as `owasp-web: 'A1: Injection'`.

*Currently Supports*

* [OWASP Web Top 10](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/owasp_web_top10_2017.yaml)
* [OWASP Mobile Top 10](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/owasp_mobile_top10_2016.yaml)
* [OWASP MASVS](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/owasp_masvs.yaml)
* [CWE](https://github.com/ajinabraham/libsast/blob/master/libsast/standards/cwe.yaml)

### Semantic Grep

Semantic Grep uses [semgrep](https://github.com/returntocorp/semgrep), a fast and syntax-aware semantic code pattern search for many languages: like grep but for code.

Currently it supports Python, Java, JavaScript, Go and C.

Use [semgrep.dev](https://semgrep.dev/vAb) to write semantic grep rule patterns.

A sample rule for Python code looks like

```yaml
rules:
  - id: boto-client-ip
    patterns:
      - pattern-inside: boto3.client(host="...")
      - pattern-regex: '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    message: "boto client using IP address"
    languages: [python]
    severity: ERROR
    metadata:
      owasp-web: a2
      owasp-mobile: m7
      cwe: cwe-1048
      foo: Some extra metadata
```

See semgrep documentation [here](https://semgrep.dev/docs/writing-rules/rule-syntax/).

Example: [Semantic Grep Rule](https://github.com/ajinabraham/libsast/blob/master/tests/assets/rules/semantic_grep/sgrep.yaml)

Test your semgrep rules

`$ libsast -s tests/assets/rules/semantic_grep/sgrep.yaml tests/assets/files/`

## Realworld Implementations

* [njsscan](https://github.com/ajinabraham/njsscan) SAST is built with libsast pattern matcher and semantic grep.
* [nodejsscan](https://github.com/ajinabraham/nodejsscan) nodejsscan is a static security code scanner for Node.js applications.
* [MobSF](https://mobsf.github.io/Mobile-Security-Framework-MobSF/) Static Code Analyzer for Android and iOS mobile applications.
* [mobsfscan](https://github.com/MobSF/mobsfscan) mobsfscan is a static security code scanner for Mobile applications built for Android (Java, Kotlin) & iOS (Swift, Objective C).
