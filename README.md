<h1 align="center">Welcome to Nautilus PDF Tools 👋</h1>

![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e8b6f27e6b404f05b379c7690c140a3c)](https://www.codacy.com/manual/atareao/nautilus-pdf-tools?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=atareao/nautilus-pdf-tools&amp;utm_campaign=Badge_Grade)
[![CodeFactor](https://www.codefactor.io/repository/github/atareao/nautilus-pdf-tools/badge/master)](https://www.codefactor.io/repository/github/atareao/nautilus-pdf-tools/overview/master)

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg?cacheSeconds=2592000)
[![Documentation](https://img.shields.io/badge/documentation-yes-brightgreen.svg)](https://www.atareao.es/aplicacion/pdf-tools-o-modificar-pdf-en-linux/)
[![Twitter: atareao](https://img.shields.io/twitter/follow/atareao.svg?style=social)](https://twitter.com/atareao)


> A set of tools to work with PDF documents from Nautilus

[![tasker](./data/icons/tasker.svg)](https://www.atareao.es/aplicacion/tasker/)

## 🏠 [Homepage](https://github.com/atareao/nautilus-pdf-tools)

## Prerequisites

* If you install it from PPA don't worry about, becouse all the requirements are included in the package
* If you clone the repository, you need, at least, these dependecies,

Common required dependencies,

```
python3
python3-gi
python3-gi-cairo
python3-cairo
python3-pil
gir1.2-gtk-3.0
gir1.2-gdkpixbuf-2.0
gir1.2-poppler-0.18
python3-pypdf2
```

#### Only for Nautilus

```
gir1.2-nautilus-3.0
python3-nautilus
```

#### Only for Nemo

```
gir1.2-nemo-3.0
python3-nemo
```

#### Only for Caja

```
gir1.2-caja-3.0
python3-caja
```
## Installing PDF Tools

To install PDF-Tools for every one of the file managers, run next commands
in a teminal (`Ctrl+Alt+T`), depending the file manager of your distro.

### Nautilus

```
sudo add-apt-repository ppa:atareao/nautilus-extensions
sudo apt update
sudo apt install nautilus-pdf-tools
nautilus -q
```

### Nemo

```
sudo add-apt-repository ppa:atareao/nemo-extensions
sudo apt update
sudo apt install nemo-pdf-tools
nemo -q
```

### Caja

```
sudo add-apt-repository ppa:atareao/caja-extensions
sudo apt update
sudo apt install caja-pdf-tools
caja -q
```

## Contributing to Nautilus PDF Tools

To contribute to **Nautilus PDF Tools**, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push origin <project_name>/<location>`
5. Create the pull request.

Alternatively see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## 👤 Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<table>
  <tr>
    <td align="center"><a href="https://www.atareao.es"><img src="https://avatars3.githubusercontent.com/u/298055?v=4" width="100px;" alt=""/><br /><sub><b>Lorenzo Carbonell</b></sub></a><br /><a href="https://github.com/atareao/nautilus-pdf-tools/commits?author=atareao" title="Code">💻</a></td>
  </tr>
</table>

## Contact

If you want to contact me you can reach me at [atareao.es](https://www.atareao.es).

## License

This project uses the following license: [MIT License](https://choosealicense.com/licenses/mit/).
