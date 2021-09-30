with import <nixpkgs> {};

python3.pkgs.buildPythonPackage {
  name = "haha";
  propagatedBuildInputs = with python3.pkgs; [ aiohttp aiohttp-jinja2 jinja2 ];
}

