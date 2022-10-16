# This program can automatically color a latex table based on the number in each cell
# Support 2 colors for positive values and negative values respectively (usually there should not be more color, and it's easy to scale larger)

import copy

# 0. use excel to calculate the color table based on the original table
# 1. use "https://www.latex-tables.com/#" to generate latex table for color value and original data respectively
# 2. paste your color data in "color_data.txt" (in the shape of original table)
# 3. paste your original table content in "table.txt"
# 4. set the color mode
# True: there will be 2 colors that renders positive and negative colors respectively
# False: reader only based on positive color, negative values are regards as "small values"
two_color_flag = True


# 3. set the objective colors

positive_color = {
    "base": {
        "R": 255,
        "G": 255,
        "B": 255
    },
    "super": {
        "R": 237,
        "G": 145,
        "B": 145
    },
}


negative_color = {
    "base": {
        "R": 255,
        "G": 255,
        "B": 255
    },
    "super": {
        "R": 154,
        "G": 224,
        "B": 103
    },
}

max_positive_value = 0
min_negative_value = 0

# text to float number
def isNumber(text):
    try:
        a = float(text)
        return True
    except:
        return False

# only keep the tabular text from the entire latex
def get_tabular_text(text):
    token_list = text.split()
    res_tok_list = []
    start_flag = False
    for tok in token_list:
        if start_flag:
            res_tok_list.append(tok)
        if 'begin{tabular}' in tok.lower():
            start_flag = True
        if 'end{tabular}' in tok.lower():
            break

    return ' '.join(res_tok_list)


# get all the value from the text, and return the list
# color is a flag used to indicate if this is the color value
def get_value_list(text, color=True):
    global max_positive_value
    global min_negative_value
    value_list = []
    token_list = text.split()
    for tok in token_list:
        if isNumber(tok):
            num = float(tok)
            # set max value and min value
            if color and num > max_positive_value:
                max_positive_value = num
            if color and num < min_negative_value:
                min_negative_value = num
            value_list.append(num)

    return value_list


# get all the value from the text, and return the list
# return a mapping list
def get_RGB_by_number(color_value_list, original_value_list):
    global max_positive_value
    global min_negative_value

    if len(color_value_list) != len(original_value_list):
        raise Exception("the shape of color data table and original value should be the same")

    mapping_list = []

    if two_color_flag:
        for i in range(len(color_value_list)):
            value = color_value_list[i]
            if value >= 0:
                R = (positive_color['base']['R'] - (positive_color['base']['R'] - positive_color['super']['R']) / max_positive_value * value) / 255
                G = (positive_color['base']['G'] - (positive_color['base']['G'] - positive_color['super']['G']) / max_positive_value * value) / 255
                B = (positive_color['base']['B'] - (positive_color['base']['B'] - positive_color['super']['B']) / max_positive_value * value) / 255

                temp_color_code = '{\cellcolor[rgb]{' + str(R) + ',' + str(G) + ',' + str(B) + '}}'

                temp_mapping = {
                    'value': value,
                    'original_value': original_value_list[i],
                    'color_code': temp_color_code
                }

                mapping_list.append(temp_mapping)

            else:
                R = (negative_color['base']['R'] - (negative_color['base']['R'] - negative_color['super']['R']) / min_negative_value * value) / 255
                G = (negative_color['base']['G'] - (negative_color['base']['G'] - negative_color['super']['G']) / min_negative_value * value) / 255
                B = (negative_color['base']['B'] - (negative_color['base']['B'] - negative_color['super']['B']) / min_negative_value * value) / 255

                temp_color_code = '{\cellcolor[rgb]{' + str(R) + ',' + str(G) + ',' + str(B) + '}}'

                temp_mapping = {
                    'value': value,
                    'original_value': original_value_list[i],
                    'color_code': temp_color_code
                }

                mapping_list.append(temp_mapping)

        # else:
        # (not necessary)


    return mapping_list


if __name__ == "__main__":
    original_table_path = 'table.txt' # raw table
    color_value_table_path = 'color_data.txt' # the same shape of raw table, but each value is the value for coloring (not original color)
    output_table_path = 'output.txt'
    with open(original_table_path, "r") as in_file:
        ori_table_text = in_file.read()
    with open(color_value_table_path, "r") as in_file:
        color_table_text = in_file.read()

    temp_text = get_tabular_text(ori_table_text)
    ori_value_list = get_value_list(temp_text, color=False)

    temp_text = get_tabular_text(color_table_text)
    color_value_list = get_value_list(temp_text, color=True)

    # get the color mapping
    mapping_list = get_RGB_by_number(color_value_list, ori_value_list)

    colored_table_text = copy.deepcopy(ori_table_text)

    # get the original number representation
    raw_num_representation_list = []

    start_flag = False

    # generate new table text
    for tok in ori_table_text.split():
        if 'begin{tabular}' in tok.lower():
            start_flag = True
            continue
        if 'end{tabular}' in tok.lower():
            break
        if start_flag and isNumber(tok):
            for map in mapping_list:
                if map['original_value'] == float(tok):
                    temp_tok = ' ' + map['color_code'] + tok + ' '
                    colored_table_text = colored_table_text.replace(' ' + tok + ' ', temp_tok)

    # generate new table text
    for map in mapping_list:
        temp_tok = ' ' + map['color_code'] + str(map['original_value']) + ' '
        colored_table_text = colored_table_text.replace(' ' + str(map['original_value']) + ' ', temp_tok)

    with open(output_table_path, "w") as out_file:
        out_file.write(colored_table_text)
        print(colored_table_text)
