import os
import re
import yaml

NN_DIR = "/home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/src/features/code_engine/algos/nn"

# URL mapping for standard reference keys
REF_URLS = {
    "rosenblatt1958perceptron": "https://doi.org/10.1037/h0042519",
    "novikoff1962convergence": "https://doi.org/10.1007/978-1-4684-2001-2_9",
    "minsky1969perceptrons": "https://mitpress.mit.edu/9780262631111/perceptrons/",
    "rumelhart1986learning": "https://doi.org/10.1038/323533a0",
    "lecun1998gradient": "https://doi.org/10.1109/5.726791",
    "glorot2010understanding": "https://proceedings.mlr.press/v9/glorot10a.html",
    "he2015delving": "https://doi.org/10.1109/ICCV.2015.123",
    "ioffe2015batch": "https://proceedings.mlr.press/v37/ioffe15.html",
    "ba2016layer": "https://arxiv.org/abs/1607.06450",
    "vaswani2017attention": "https://arxiv.org/abs/1706.03762",
    "kingma2014adam": "https://arxiv.org/abs/1412.6980",
    "loshchilov2017decoupled": "https://arxiv.org/abs/1711.05101",
    "srivastava2014dropout": "https://jmlr.org/papers/v15/srivastava14a.html",
    "huang2016deep": "https://doi.org/10.1007/978-3-319-46493-0_39",
    "zhang2017mixup": "https://arxiv.org/abs/1710.09412",
    "yun2019cutmix": "https://doi.org/10.1109/ICCV.2019.00612",
    "goodfellow2014explaining": "https://arxiv.org/abs/1412.6572",
    "madry2017towards": "https://arxiv.org/abs/1706.06083",
    "lin2017feature": "https://doi.org/10.1109/CVPR.2017.106",
    "ren2015faster": "https://arxiv.org/abs/1506.01497",
    "redmon2016you": "https://doi.org/10.1109/CVPR.2016.91",
    "bodla2017soft": "https://doi.org/10.1109/ICCV.2017.593",
    "carion2020end": "https://doi.org/10.1007/978-3-030-58452-8_13",
    "he2017mask": "https://doi.org/10.1109/ICCV.2017.322",
    "tian2019fcos": "https://doi.org/10.1109/ICCV.2019.00972",
    "werbos1990backpropagation": "https://doi.org/10.1109/5.58337",
    "hochreiter1997long": "https://doi.org/10.1162/neco.1997.9.8.1735",
    "cho2014learning": "https://doi.org/10.3115/v1/D14-1179",
    "schuster1997bidirectional": "https://doi.org/10.1109/78.650093",
    "sutskever2014sequence": "https://arxiv.org/abs/1409.3215",
    "bahdanau2014neural": "https://arxiv.org/abs/1409.0473",
    "luong2015effective": "https://doi.org/10.18653/v1/D15-1166",
    "bengio2015scheduled": "https://arxiv.org/abs/1506.03099",
    "wu2016google": "https://arxiv.org/abs/1609.08144",
    "vinyals2015pointer": "https://arxiv.org/abs/1506.03134",
    "see2017get": "https://doi.org/10.18653/v1/P17-1099",
    "oord2016wavenet": "https://arxiv.org/abs/1609.03499",
    "bai2018empirical": "https://arxiv.org/abs/1803.01271",
    "tan2019efficientnet": "https://arxiv.org/abs/1905.11946",
    "ronneberger2015u": "https://doi.org/10.1007/978-3-319-24574-4_28",
    "dai2017deformable": "https://doi.org/10.1109/ICCV.2017.89",
    "liu2022convnet": "https://doi.org/10.1109/CVPR52688.2022.01167",
    "hu2018squeeze": "https://doi.org/10.1109/CVPR.2018.00745",
    "szegedy2015going": "https://doi.org/10.1109/CVPR.2015.7298594",
    "sandler2018mobilenetv2": "https://doi.org/10.1109/CVPR.2018.00474",
    "he2016deep": "https://doi.org/10.1109/CVPR.2016.90",
    "lin2013network": "https://arxiv.org/abs/1312.4400",
    "shi2016real": "https://doi.org/10.1109/CVPR.2016.207",
    "chollet2017xception": "https://doi.org/10.1109/CVPR.2017.195",
    "yu2015multi": "https://arxiv.org/abs/1511.07122",
    "park2019specaugment": "https://arxiv.org/abs/1904.08779",
    "wei2019eda": "https://doi.org/10.18653/v1/D19-1670",
    "sennrich2015improving": "https://doi.org/10.18653/v1/P16-1009",
    "xie2020unsupervised": "https://arxiv.org/abs/1904.12848",
    "sohn2020fixmatch": "https://arxiv.org/abs/2001.07685",
    "prechelt1998early": "https://doi.org/10.1007/3-540-49430-8_3",
    "cubuk2019autoaugment": "https://doi.org/10.1109/CVPR.2019.00019",
    "cubuk2020randaugment": "https://arxiv.org/abs/1909.13719",
    "salimans2016weight": "https://arxiv.org/abs/1602.07868",
    "miyato2018spectral": "https://arxiv.org/abs/1802.05957",
    "wu2018group": "https://doi.org/10.1007/978-3-030-01261-8_1",
    "ulyanov2016instance": "https://arxiv.org/abs/1607.08022",
    "zhang2019root": "https://arxiv.org/abs/1910.07467",
    "xiong2020layer": "https://arxiv.org/abs/2002.04745",
    "deghani2023scaling": "https://arxiv.org/abs/2302.05442",
    "team2024gemma": "https://arxiv.org/abs/2403.08295"
}

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    cleaned_lines = []
    in_docstring = False
    docstring_char = None

    for line in lines:
        stripped = line.strip()
        
        # Track triple quote boundaries
        if '"""' in line:
            count = line.count('"""')
            if count % 2 == 1:
                in_docstring = not in_docstring
        elif "'''" in line:
            count = line.count("'''")
            if count % 2 == 1:
                in_docstring = not in_docstring

        if in_docstring:
            # Inside docstrings, check if it is a reference line that can be converted to URL
            if stripped.startswith('- ') and not stripped.startswith('- http') and not stripped.startswith('- len') and not stripped.startswith('- all') and not stripped.startswith('- input') and not stripped.startswith('- output') and not stripped.startswith('- ADAPTER') and not stripped.startswith('- ALGO') and not stripped.startswith('- type') and not stripped.startswith('- neural') and not stripped.startswith('- nn.'):
                key = stripped[2:].strip().strip('"').strip("'")
                if key in REF_URLS:
                    indent = line[:line.index('-')]
                    cleaned_lines.append(f'{indent}- "{REF_URLS[key]}"')
                    continue
                elif not key.startswith("http") and re.match(r'^[a-z]+[0-9]{4}[a-z0-9_]*$', key):
                    # Convert key to a search URL if not in dict
                    indent = line[:line.index('-')]
                    cleaned_lines.append(f'{indent}- "https://doi.org/search?q={key}"')
                    continue
            cleaned_lines.append(line)
        else:
            # Outside docstrings: remove inline comments
            if '#' in line:
                # Check if hash is part of a string literal or purely a comment
                # Simple check: line before #
                hash_pos = line.find('#')
                # Count quotes before hash
                before = line[:hash_pos]
                single_quotes = before.count("'") - before.count("\\'")
                double_quotes = before.count('"') - before.count('\\"')
                
                if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                    # It's a genuine inline comment!
                    code_part = line[:hash_pos].rstrip()
                    if code_part:
                        cleaned_lines.append(code_part)
                    # If line was ONLY a comment, skip it
                    continue
            cleaned_lines.append(line)

    new_content = '\n'.join(cleaned_lines)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    modified_count = 0
    total_files = 0
    for root, dirs, files in os.walk(NN_DIR):
        for file in files:
            if file == "impl.py":
                total_files += 1
                fp = os.path.join(root, file)
                if clean_file(fp):
                    modified_count += 1
                    print(f"Cleaned: {fp}")

    print(f"Total checked: {total_files}, Modified: {modified_count}")

if __name__ == "__main__":
    main()
