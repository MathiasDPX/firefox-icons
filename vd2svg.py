# holy vibecoding

from xml.etree import ElementTree as ET
from pathlib import Path
from typing import Union, Optional

def convert_vector_drawable_to_svg(
    input_path: Union[str, Path], 
    output_path: Optional[Union[str, Path]] = None
) -> str:
    """
    Convert Android VectorDrawable XML to SVG format.
    
    Args:
        input_path: Path to the input Android VectorDrawable XML file
        output_path: Optional path to save the SVG file. If None, returns SVG content as string
        
    Returns:
        SVG content as a string
        
    Notes:
        - Converts <vector>, <group>, <path>, <clip-path>, and Android <gradient> elements
        - Android color values with alpha (e.g. #FFF05032) are converted with opacity
        - Gradients use gradientUnits="userSpaceOnUse"
        - This is a best-effort conversion; some Android-specific attributes may be approximated
    """
    input_path = Path(input_path)
    
    ns = {"android": "http://schemas.android.com/apk/res/android", "aapt": "http://schemas.android.com/aapt"}

    def android_attr(elem, name):
        """Extract Android attribute from element."""
        return elem.get(f'{{{ns["android"]}}}{name}')

    def normalize_color(col):
        """Convert Android color format to SVG format with opacity."""
        if not col:
            return (None, None)
        col = col.strip()
        if not col.startswith('#'):
            return (col, 1.0)
        hexv = col[1:]
        if len(hexv) == 8:  # AARRGGBB
            a = int(hexv[0:2], 16) / 255.0
            rgb = '#' + hexv[2:]
            return (rgb, a)
        if len(hexv) == 6:
            return ('#' + hexv, 1.0)
        return (col, 1.0)

    def convert_gradient(grad_elem, grad_count):
        """Convert Android gradient to SVG linearGradient."""
        grad_count += 1
        gid = f'g{grad_count}'
        sx = grad_elem.get(f'{{{ns["android"]}}}startX') or grad_elem.get('startX') or "0"
        sy = grad_elem.get(f'{{{ns["android"]}}}startY') or grad_elem.get('startY') or "0"
        ex = grad_elem.get(f'{{{ns["android"]}}}endX') or grad_elem.get('endX') or "0"
        ey = grad_elem.get(f'{{{ns["android"]}}}endY') or grad_elem.get('endY') or "0"
        
        svg = [f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}">']
        
        for item in grad_elem.findall('item') + grad_elem.findall(f'{{{ns["android"]}}}item'):
            offset = item.get(f'{{{ns["android"]}}}offset') or item.get('offset') or '0'
            color = item.get(f'{{{ns["android"]}}}color') or item.get('color') or '#000000'
            rgb, opa = normalize_color(color)
            if opa is None:
                opa = 1.0
            svg.append(f'<stop offset="{offset}" stop-color="{rgb}" stop-opacity="{opa:.3f}" />')
        
        svg.append('</linearGradient>')
        return gid, '\n'.join(svg), grad_count

    def process_path_element(child, grad_map, svg_parts, grad_count):
        """Process a path element and return SVG path string."""
        pdata = child.get(f'{{{ns["android"]}}}pathData') or child.get('pathData') or ''
        fill = child.get(f'{{{ns["android"]}}}fillColor') or child.get('fillColor')
        stroke = child.get(f'{{{ns["android"]}}}strokeColor') or child.get('strokeColor')
        stroke_w = child.get(f'{{{ns["android"]}}}strokeWidth') or child.get('strokeWidth')
        
        # Check for aapt:attr fillColor with gradient
        used_fill = ''
        for aapt_attr in child.findall(f'{{{ns["aapt"]}}}attr'):
            if aapt_attr.get('name', '').endswith('fillColor'):
                grad = aapt_attr.find('gradient') or aapt_attr.find(f'{{{ns["android"]}}}gradient')
                if grad is not None:
                    gid = grad_map.get(id(grad))
                    if gid is None:
                        gid, svg_grad, grad_count = convert_gradient(grad, grad_count)
                        grad_map[id(grad)] = gid
                        svg_parts.insert(1, svg_grad)
                    used_fill = f'url(#{gid})'
        
        # Handle fill
        if not used_fill and fill:
            rgb, opa = normalize_color(fill)
            style_fill = f' fill="{rgb}"'
            if opa is not None and opa < 1.0:
                style_fill += f' fill-opacity="{opa:.3f}"'
        else:
            style_fill = f' fill="{used_fill}"' if used_fill else ''
        
        # Handle stroke
        style_stroke = ''
        if stroke:
            s_rgb, s_opa = normalize_color(stroke)
            style_stroke += f' stroke="{s_rgb}"'
            if s_opa is not None and s_opa < 1.0:
                style_stroke += f' stroke-opacity="{s_opa:.3f}"'
        if stroke_w:
            style_stroke += f' stroke-width="{stroke_w}"'
        
        return f'<path d="{pdata}"{style_fill}{style_stroke} />', grad_count

    def process_group(g, grad_map, svg_parts, grad_count, clip_count):
        """Process a group element recursively."""
        parts = ['<g>']
        
        for child in g:
            tag = child.tag
            if tag.endswith('clip-path'):
                clip_count += 1
                cid = f'c{clip_count}'
                pdata = child.get(f'{{{ns["android"]}}}pathData') or child.get('pathData') or ''
                svg_parts.insert(1, f'<clipPath id="{cid}"><path d="{pdata}" /></clipPath>')
                parts[0] = f'<g clip-path="url(#{cid})">'
            elif tag.endswith('path'):
                path_svg, grad_count = process_path_element(child, grad_map, svg_parts, grad_count)
                parts.append(path_svg)
            else:
                if len(child) > 0:
                    group_svg, grad_count, clip_count = process_group(child, grad_map, svg_parts, grad_count, clip_count)
                    parts.append(group_svg)
        
        parts.append('</g>')
        return '\n'.join(parts), grad_count, clip_count

    # Parse the XML file
    tree = ET.parse(input_path)
    root = tree.getroot()

    # Extract dimensions
    svg_w = android_attr(root, "viewportWidth") or android_attr(root, "width") or "438"
    svg_h = android_attr(root, "viewportHeight") or android_attr(root, "height") or "438"

    # Start building SVG
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{android_attr(root,"width") or svg_w}" height="{android_attr(root,"height") or svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns:xlink="http://www.w3.org/1999/xlink">',
        '<defs>'
    ]

    grad_map = {}
    grad_count = 0
    clip_count = 0

    # Find gradients inside aapt:attr fillColor blocks
    for elem in root.iter():
        for aapt_attr in elem.findall(f'{{{ns["aapt"]}}}attr'):
            name = aapt_attr.get('name')
            if name and name.endswith('fillColor'):
                grad = aapt_attr.find('gradient') or aapt_attr.find(f'{{{ns["android"]}}}gradient')
                if grad is not None:
                    gid, svg_grad, grad_count = convert_gradient(grad, grad_count)
                    grad_map[id(grad)] = gid
                    svg_parts.append(svg_grad)

    # Handle standalone gradients
    for grad in root.findall('.//gradient'):
        if id(grad) not in grad_map:
            gid, svg_grad, grad_count = convert_gradient(grad, grad_count)
            grad_map[id(grad)] = gid
            svg_parts.append(svg_grad)

    svg_parts.append('</defs>')

    # Process top-level elements
    for child in root:
        if child.tag.endswith('group'):
            group_svg, grad_count, clip_count = process_group(child, grad_map, svg_parts, grad_count, clip_count)
            svg_parts.append(group_svg)
        elif child.tag.endswith('path'):
            path_svg, grad_count = process_path_element(child, grad_map, svg_parts, grad_count)
            svg_parts.append(path_svg)

    svg_parts.append('</svg>')
    svg_content = ''.join(svg_parts)

    # Save to file if output path is provided
    if output_path:
        output_path = Path(output_path)
        output_path.write_text(svg_content, encoding='utf-8')
        print(f"Saved SVG to: {output_path}")

    return svg_content


# Example usage:
if __name__ == "__main__":
    import sys

    args = sys.argv
    del args[0]

    print(args)