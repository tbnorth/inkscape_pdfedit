"""
inkscape_pdfedit.py - export a pdf to multiple images, load as
layers in Inkscape.

Terry Brown, Terry_N_Brown@yahoo.com, Tue Nov 17 16:39:28 2015
"""

import argparse
import os
import sys
from copy import deepcopy
from lxml import etree
from glob import glob

NS = {
    'svg': "http://www.w3.org/2000/svg",
    'xlink': "http://www.w3.org/1999/xlink",
    'inkscape': "http://www.inkscape.org/namespaces/inkscape",
}

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
    if True or not os.path.exists(os.path.join(dirname, basename)):
        make_imgs_svg(opt)
    else:
        make_pdf(opt)

def make_imgs_svg(opt):
    """make_imgs_svg - extract images and build pdf

    :param argparse Namespace opt: options
    """

    if not os.path.exists(os.path.join(opt.dirname, opt.basename)):
        os.mkdir(os.path.join(opt.dirname, opt.basename))
    cmd = "convert -density 300 %s %s" % (
        opt.filename, os.path.join(opt.dirname, opt.basename, "%s.png" % opt.basename))
    print(cmd)
    # os.system(cmd)
    cmd = "mogrify -flatten %s" % (
        os.path.join(opt.dirname, opt.basename, "%s-*.png" % opt.basename))
    print(cmd)
    # os.system(cmd)
    
    svg_template = os.path.join(
        os.path.dirname(__file__),
        'inkscape_pdf_template.svg'
    )
    dom = etree.parse(open(svg_template))
    parent_map = {c:p for p in dom.iter() for c in p}
    svg_file = os.path.join(opt.dirname, opt.basename, "%s.svg" % opt.basename)
    opt.svg_file = svg_file
    #layer = dom.xpath(".//svg:g[@id='layer_0']", namespaces=NS)[0]
    #img_count = len(glob(os.path.join(opt.dirname, opt.basename, "%s-*.png" % opt.basename)))
    for n in range(3):
        break
        if n == 0:
            new_layer = layer
        else:
            new_layer = deepcopy(layer)
            parent_map[layer].append(new_layer)
        new_layer.set('id', 'layer_%04d' % (n+1))
        new_layer.set('{%s}label' % NS['inkscape'], 'Page %04d' % (n+1))
        # img = new_layer.xpath(".//svg:image", namespaces=NS)[0]
        # img.set('id', 'img_%04d' % (n+1))
        # img.set('{%s}href' % NS['xlink'], 'file://./%s-%d.png' % (opt.basename, n))
    dom.write(svg_file)
    
def main():
    opt = make_parser().parse_args()
    
    proc_file(opt)

if __name__ == '__main__':
    main()
