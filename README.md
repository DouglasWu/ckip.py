# CKIP.py
This project is forked from [jason2506/ckip.py](https://github.com/jason2506/ckip.py)

The purpose of the modification is to extract word-to-word relations from a parsed sentence. For example, when you have a tree text:
```
S(experiencer:NP(Head:Nhaa:我們)|quantity:Dab:都|Head:VK1:喜歡|goal:NP(property:V‧的(head:VH11:美麗|Head:DE:的)|Head:Nab:蝴蝶))
```
You can extract the relations:
```
experiencer Nhaa 我們
Head[S] VK1 喜歡
---------------------------
quantity Dab 都
Head[S] VK1 喜歡
---------------------------
Head[S] VK1 喜歡
goal Nab 蝴蝶
---------------------------
property VH11 美麗
Head[NP] Nab 蝴蝶
---------------------------
head[V•的] VH11 美麗
Head DE 的
---------------------------
```

## Modifications

1. I moved the `contruct_parsing_tree` function in ckip.py to another file and let the CKIPParser only return the raw tree text.

2. I modified the `contruct_parsing_tree` function so that each node keeps the **role** information and has a unique **id**.

3. According to this document: [句結構樹中的語意角色](http://ckip.iis.sinica.edu.tw/CKIP/tr/201301_20140813.pdf),
'Head' is the syntactic center of a sentence while 'head' is the semantic center. When 'Head' and 'head' appear in the same subtree, I choose 'head' to represent the subtree.

## Example
For example usage, see [demo.ipynb](demo.ipynb)