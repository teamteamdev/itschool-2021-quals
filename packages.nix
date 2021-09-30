{
  binPackages = pkgs: with pkgs; [
  ];

  pythonPackages = self: with self; [
    aiohttp
    aiohttp-jinja2
    jinja2
    pyjwt
  ];
}
