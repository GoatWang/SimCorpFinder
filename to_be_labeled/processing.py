import pandas as pd
import os
import json
from collections import OrderedDict
import random
df_matching = pd.read_csv('targets.csv', header=None)
df_matching.columns = ['ori_target', 'target']

filenames = os.listdir(os.path.join('..', 'processed_data'))
filenames = [os.path.join('..', 'processed_data', f) for f in filenames if f.endswith('.json')]

all_count = 0
df_count = []
for num, filename in list(enumerate(filenames)):
    with open(filename, 'r', encoding='utf8') as f:
        comp = json.load(f)

    filename = filename.replace('.json', '').split("\\")[2]
    print(num, filename)
    new_target = list(df_matching[df_matching['ori_target'] == filename]['target'])[0]
    # print(new_target)
    # new_target = list(df_matching[df_matching['ori_target'] == filename]['target'])
    # print(new_target)

    comp['target'] = new_target
    comp['compLi'].pop(comp['compLi'].index(new_target))

    compLi_label = []
    for item in comp['compLi']:
        compLi_label.append(OrderedDict([('name', item), ('home_website',""), ('products', []), ('score', 0)]))
    comp['compLi_label'] = compLi_label
    
    df_comp_detail = pd.DataFrame(comp['compLi_detail'])
    idx = df_comp_detail[df_comp_detail['name'] == new_target].index[0]
    df_comp_detail.drop(idx, inplace=True)
    compLi_detail = []
    for item in list(df_comp_detail.T.to_dict().values()):
        compLi_detail.append(OrderedDict([('name', item['name']),('sic', item['sic']),('selected', item['selected'])]))
    comp['compLi_detail'] = compLi_detail



    ourput_dict = []
    ourput_dict.append(('target', comp['target']))
    ourput_dict.append(('target_ori', filename))
    ourput_dict.append(('compLi_Len', len(comp['compLi'])))
    ourput_dict.append(('sic', comp['sic']))
    
    ourput_dict.append(('keywords_ori', comp['keywords_ori']))

    ourput_dict.append(('keywords', OrderedDict([
        ("Keywords", comp['keywords']['Keywords']),
        ("KeyWords(Emphasize)", comp['keywords']['KeyWords(Emphasize)']),
        ("KeyWords(Filtered)", comp['keywords']['KeyWords(Filtered)'])
    ])))

    ourput_dict.append(('compLi', comp['compLi']))
    ourput_dict.append(('target_label',  OrderedDict([('name',comp['target']), ('home_website', ""), ('products',[])])))
    ourput_dict.append(('compLi_label',  comp['compLi_label']))
    
    ourput_dict.append(('compLi_detail', comp['compLi_detail']))
    

    
    # new_filename = new_target+'.json'
    # if new_filename in os.listdir('jsonfile'):
    #     new_filename = new_target + str(random.randint(0, 100)) + ".json"

    # output_json = json.dumps(OrderedDict(ourput_dict), ensure_ascii=False)
    # with open(os.path.join('jsonfile', new_filename), 'w', encoding='utf8') as f:
    #     f.write(output_json)

    count_dict = OrderedDict([('filename', filename), ('name', comp['target']), ('count', len(comp['compLi']))])
    df_count.append(count_dict)
    all_count+=len(comp['compLi']) + 1

print("target companies:", len(filenames))
print("toatl companies: ", all_count)
print("toatl hours: ", (all_count*3)/60)
print("salary per person: ", ((all_count*3)/60)*170)
print("total salary(3 labor): ", ((all_count*3)/60)*170*3)

df_count = pd.DataFrame(df_count)
print(df_count[df_count['count'] > 100])
print(sum(df_count[df_count['count'] < 100]['count']))
print(len(df_count[df_count['count'] < 100]))
