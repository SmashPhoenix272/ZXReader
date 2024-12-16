import sys
import os

# Add necessary paths
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)

from QTEngine.src.text_processing import convert_to_sino_vietnamese, process_paragraph
from QTEngine.src.data_loader import DataLoader

def test_mapping():
    # Test text
    test_text = """001 0分狂魔
千叶市公立小学，一年级a班。
千叶市公立小学，一年级a班。
千叶市公立小学，一年级a班。
年轻的大姐姐老师站在上面，手捧一摞试卷，面带微笑看着下方的孩子们......
她的心情很好，因为在这些孩子们中，有个段位明显高于平均水平的小学生，能够教导这样的学生，老师很自豪。
“测验成绩出来了哦，这次大家都考得不错，”大姐姐老师面带微笑，满面红光，“在这里要特意表扬一下雪之下，100分，大家鼓掌——”
“真厉害呢雪乃酱，又是满分，来拿你的试卷吧。”
随着掌声，教室里孩子们目光整齐划一看向那个默默起身的小萝莉，脸庞娇艳清丽、黑发飘飘，还是个七岁的小女孩就展现出自己的美貌与魅力，就是神色有点淡定，仿佛拿到一百分是再简单不过的事情。
无形中装了个逼啊。
角落里的野比大雄单手托腮，无聊的把玩手中铅笔，默默听着周围同学们的窃窃私语。
“又是100分，好厉害。”
“好像每次考试她都是100分吧？”
"""
    
    # Load data using DataLoader
    data_loader = DataLoader()
    names2, names, viet_phrase, chinese_phien_am, loading_info = data_loader.load_data()

    # Test paragraph processing
    result, mapping = process_paragraph(test_text, names2, names, viet_phrase, chinese_phien_am)
    
    # Print original and translated text with mapping information
    sys.stdout.buffer.write(("Original Text:\n" + test_text + "\n").encode('utf-8'))
    sys.stdout.buffer.write(("Translated Text:\n" + result + "\n").encode('utf-8'))
    sys.stdout.buffer.write("Mapping Information:\n".encode('utf-8'))
    for block in mapping.blocks:
        sys.stdout.buffer.write((f"Original: '{block.original}' ({block.orig_start}-{block.orig_end})\n").encode('utf-8'))
        sys.stdout.buffer.write((f"Translated: '{block.translated}' ({block.trans_start}-{block.trans_end})\n").encode('utf-8'))
        sys.stdout.buffer.write(("-" * 50 + "\n").encode('utf-8'))
    
    # Prepare to save mapping information
    mapping_info = []
    for block in mapping.blocks:
        mapping_info.append(f"Original: '{block.original}' ({block.orig_start}-{block.orig_end})\n")
        mapping_info.append(f"Translated: '{block.translated}' ({block.trans_start}-{block.trans_end})\n")
        mapping_info.append("--------------------------------------------------\n")

    # Save output to markdown file
    with open('test_results.md', 'w', encoding='utf-8') as f:
        f.write('# Test Results\n')
        f.write('## Test Mapping Result\n')
        f.write(f'\n{result}\n')
        f.write('## Mapping Information\n')
        f.writelines(mapping_info)
    return result

if __name__ == "__main__":
    result = test_mapping()