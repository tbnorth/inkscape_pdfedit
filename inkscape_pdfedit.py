"""
inkscape_pdfedit.py - export a pdf to multiple images, load as
layers in Inkscape.

Terry Brown, Terry_N_Brown@yahoo.com, Tue Nov 17 16:39:28 2015
"""

import argparse
import os
import sys
from copy import deepcopy
from xml.etree import ElementTree
from glob import glob

SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
INKSCAPE = "http://www.inkscape.org/namespaces/inkscape"
SODIPODI = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
def make_parser():
     
     parser = argparse.ArgumentParser(
         description="inkscape_pdfedit.py - export a pdf to multiple images, "
                     "load as layers in Inkscape",
         formatter_class=argparse.ArgumentDefaultsHelpFormatter
     )
     
     # parser.add_argument("--foo", action='store_true',
     #     help="help"
     # )
     parser.add_argument('filename', type=str, help="PDF filename")

     return parser
 
def proc_file(opt):
    """proc_file - do next step in process

    :param argparse Namespace opt: options, updated
    """

    dirname = os.path.dirname(opt.filename)
    basename = os.path.basename(opt.filename)[:-4]  # remove '.pdf'
    opt.dirname = dirname
    opt.basename = basename
    if not os.path.exists(os.path.join(dirname, basename)):
        make_imgs_svg(opt)
    else:
        make_pdf(opt)

def make_imgs_svg(opt):
    """make_imgs_svg - extract images and build svg

    :param argparse Namespace opt: options
    """

    if not os.path.exists(os.path.join(opt.dirname, opt.basename)):
        os.mkdir(os.path.join(opt.dirname, opt.basename))
    cmd = "convert -density 300 %s %s" % (
        opt.filename, os.path.join(opt.dirname, opt.basename, "%s-%%04d.png" % opt.basename))
    print(cmd)
    os.system(cmd)
    cmd = "mogrify -flatten %s" % (
        os.path.join(opt.dirname, opt.basename, "%s-*.png" % opt.basename))
    print(cmd)
    os.system(cmd)

    svg_template = os.path.join(
        os.path.dirname(__file__),
        'inkscape_pdf_template.svg'
    )
    dom = ElementTree.parse(open(svg_template))
    parent_map = {c:p for p in dom.iter() for c in p}
    svg_file = os.path.join(opt.dirname, opt.basename, "%s.svg" % opt.basename)
    layer = dom.find(".//{%s}g[@id='layer_0']" % SVG)
    img_count = len(glob(os.path.join(opt.dirname, opt.basename, "%s-*.png" % opt.basename)))
    for n in range(img_count):
        if n == 0:
            new_layer = layer
        else:
            new_layer = deepcopy(layer)
            parent_map[layer].insert(0, new_layer)
            new_layer.set('style', 'display:none;')
        new_layer.set('id', 'layer_%04d' % (n+1))
        new_layer.set('{%s}label' % INKSCAPE, 'Page %04d' % (n+1))
        img = new_layer.find(".//{%s}image" % SVG)
        img.set('id', 'img_%04d' % (n+1))
        fileref = 'file://%s-%04d.png' % (os.path.join(os.path.abspath(opt.dirname), opt.basename, opt.basename), n)
        img.set('{%s}href' % XLINK, fileref)
        img.set('{%s}insensitive' % SODIPODI, "true")
    dom.write(svg_file)
    

def make_pdf(opt):
    """make_pdf - save layers and make pdf

    :param argparse Namespace opt: options
    """

    img_count = len(glob(os.path.join(opt.dirname, opt.basename, "%s-*.png" % opt.basename)))

    # set all layers visible
    svg_file = os.path.join(opt.dirname, opt.basename, "%s.svg" % opt.basename)
    dom = ElementTree.parse(open(svg_file))
    for n in range(img_count):
        layer = dom.find(".//{%s}g[@id='layer_%04d']" % (SVG, (n+1)))
        layer.set('style', '')
    dom.write(svg_file)

    for n in range(img_count):
        cmd = ("inkscape --without-gui --file=%s.svg --export-pdf=%s_%04d.pdf "
               "--export-id=%s --export-id-only" % (
            os.path.join(opt.basename, opt.basename),
            os.path.join(opt.basename, opt.basename), n,
            'layer_%04d' % (n+1)))
        print(cmd)
        os.system(cmd)

    cmd = ("gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER "
        "-sOutputFile=%s_edit.pdf %s" % (
        os.path.join(opt.basename, opt.basename),
        ' '.join("%s_%04d.pdf" % (os.path.join(opt.basename, opt.basename), n)
                 for n in range(img_count)
        )))
    print(cmd)
    os.system(cmd)

def main():
    opt = make_parser().parse_args()
    
    proc_file(opt)

if __name__ == '__main__':
    main()
