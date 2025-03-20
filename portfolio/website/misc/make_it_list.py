import re

def process_markdown(lines):
    lines = lines.split("\n")
    
    output = []
    inside_func_req = False
    inside_unfunc_req = False
    detail_opened = False
    
    for line in lines:
        if "Functional Requirements" in line:
            inside_func_req = True
            output.append(line.strip().replace('-','#'))
            output.append('\n')
            continue
        elif "Non-functional Requirements" in line:
            inside_func_req = False
            inside_unfunc_req = True
            if detail_opened:
                output.append('</blockquote>\n')
                output.append('</details>\n')
                detail_opened = False
            output.append('\n # ')
            output.append(line.strip()[2:])
            output.append('\n')
            continue
        
        if inside_func_req:
            if re.match(r'\s*- \d+\.\d+\.\d+\. ', line.strip()):
                if detail_opened:
                    output.append('</blockquote>\n')
                    output.append('</details>\n\n')
                output.append(f'<details><summary>{line.strip()[2:]}</summary><blockquote>\n\n')
                detail_opened = True
                continue
            elif re.match(r'\s*- \d+\.\d+\. ', line.strip()):
                if detail_opened:
                    output.append('</blockquote>\n')
                    output.append('</details>\n\n')
                    detail_opened = False
                output.append('\n')
                output.append(line.strip().replace('-','##'))
                output.append('\n')
                output.append('\n')
                continue
        elif inside_unfunc_req:
            if re.match(r'\s*- \d+\.\d+\. ', line.strip()):
                if detail_opened:
                    output.append('</blockquote>\n')
                    output.append('</details>\n\n')
                output.append(f'<details><summary>{line.strip()[2:]}</summary><blockquote>\n\n')
                detail_opened = True
                continue
        
        # Add indentation for items with depth 5 or more (e.g., 1.2.3.4.1)
        if (inside_func_req or inside_unfunc_req) and len(line.strip()) > 1:
            # Check if it's a requirement with 5 or more parts
            depth_match = re.match(r'\s*- (\d+\.\d+\.\d+\.\d+\.\d+.*)', line.strip())
            if depth_match:
                # Add indentation for deep items
                indented_line = "     " + line.strip() + '\n'
                output.append(indented_line)
            else:
                output.append(line.strip() + '\n')
        else:
            output.append(line)
    
    if detail_opened:
        output.append('</details>\n')
    
    output_text = ''.join(output)

    return output_text