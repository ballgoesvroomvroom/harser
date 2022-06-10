# Harser

My own custom text to HTML parser with a terrible name choice.<br>
Used for my own [portfolio page](https://github.com/ballgoesvroomvroom/weter).<br>

With its own semantic layout consisting of `<article>` and `<section>` tags.

## Syntax

`# header`: similar to markdown, **H1** headings automatically create a new article, **H2** onwards creates a new section<br>
**H1** headings include an additional `[content]` afterwards followed by a space to denote the **id** for the **article** to enable anchor links

`{#header}`: creates a new header with its level corresponding to the amount of hashes without creating a new section<br>

`{`: creates a new unstyled **div** element<br>

`{ [l-r]`: creates a directed **div** (div as a flex container); directions can only include "l-r" (left to right) and "r-l" (right to left)<br>

`}`: closes any created **div**s<br>

<code>\`</code>: creates an **inline code** statement

<code>\```</code>: creates a **code** block

`[link_text](link_path)`: similarly to markdown, creates a **hyperlink**

`![alt_text](image_path)[caption]`: similarly to markdown, creates an **image** wrapped in `<figure>` with the `<figcaption>` element with its content being the caption proprety

`{filename}[file description](file_path)`: creates a new downloadable file card
![image of how downloadable file card looks](./static/filecard.png)

## To note
Uses `input.txt` in the parent directory of `/src`, aka root directory of this repository<br>
Outputs to `o.html` in the same directory as `input.txt`
