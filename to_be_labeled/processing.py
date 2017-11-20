import pandas as pd
import os
import json
from collections import OrderedDict
df_matching = pd.read_csv('targets.csv', header=None)
df_matching.columns = ['ori_target', 'target']

filenames = os.listdir(os.path.join('..', 'processed_data'))
filenames = [os.path.join('..', 'processed_data', f) for f in filenames if f.endswith('.json')]

for num, filename in list(enumerate(filenames)):
    with open(filename, 'r', encoding='utf8') as f:
        comp = json.load(f)

    filename = filename.replace('.json', '').split("\\")[2]
    print(num, filename)
    new_target = list(df_matching[df_matching['ori_target'] == filename]['target'])[0]
    # new_target = list(df_matching[df_matching['ori_target'] == filename]['target'])
    # print(new_target)

    comp['target'] = new_target
    comp['compLi'].pop(comp['compLi'].index(new_target))

    df_comp_detail = pd.DataFrame(comp['compLi_detail'])
    idx = df_comp_detail[df_comp_detail['name'] == new_target].index[0]
    df_comp_detail.drop(idx, inplace=True)
    comp['compLi_detail'] = list(df_comp_detail.T.to_dict().values())

    ourput_dict = []
    ourput_dict.append(('target', comp['target']))
    ourput_dict.append(('target_ori', filename))
    ourput_dict.append(('sic', comp['sic']))
    ourput_dict.append(('keywords_ori', comp['keywords_ori']))

    ourput_dict.append(('keywords', {
        "Keywords": comp['keywords']['Keywords'],
        "KeyWords(Emphasize)": comp['keywords']['KeyWords(Emphasize)'],
        "KeyWords(Filtered)": comp['keywords']['KeyWords(Filtered)']
    }))

    ourput_dict.append(('compLi', comp['compLi']))
    ourput_dict.append(('compLi_detail', [{'name':detail['name'], 'sic':detail['sic'], 'selected':detail['selected']} for detail in comp['compLi_detail']]))
    
    output_json = json.dumps(OrderedDict(ourput_dict))
    with open(os.path.join('jsonfile', new_target+'.json'), 'w', encoding='utf8') as f:
        f.write(output_json)