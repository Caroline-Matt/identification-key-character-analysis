"""
Script Name: KeyFeatureAnalysis.py

Author: Wen-Xuan Yue
ORCID: https://orcid.org/0009-0001-1298-6626
Affiliation: School of Life Sciences, Lanzhou University
Date: 2026-06-10

## Description

This script performs quantitative analysis of morphological characters
used in the angiosperm family-level identification keys of
*Key to the Vascular Plants of Inner Mongolia*.

The program identifies individual key entries, classifies morphological
characters using predefined keyword dictionaries, estimates character
frequencies, and evaluates uncertainty using bootstrap resampling.

## Input

pdfToTxt_output.txt

## Output

检索表关键词统计.xlsx

## Workflow

1. Identify and extract key entries (e.g., 1a., 1b., 2a., 2b.).
2. Classify organ-level morphological characters.
3. Classify floral character categories.
4. Perform bootstrap resampling (1000 iterations).
5. Estimate character frequencies and 95% confidence intervals.
6. Compare frequency differences among character categories using
   bootstrap distributions.

## Statistical Principles

1. Within a single key entry, each organ category is counted at most once.
2. Within a single key entry, each floral character category is counted
   at most once.
3. Presence of any predefined keyword is considered evidence for the
   corresponding category.
4. Statistical comparisons are based on bootstrap-derived confidence
   intervals (95% CI).

## Software Environment

Python 3.11

## Required Packages

numpy
pandas
openpyxl

## Project Context

This script was developed for the quantitative analysis of
morphological characters used in the angiosperm family-level
identification keys of *Key to the Vascular Plants of Inner Mongolia*.

The statistical unit is the individual key entry rather than the total
number of keyword occurrences within the text.

## Interpretation

The results reflect the relative frequency with which different
morphological characters are employed in taxonomic identification keys.

They should not be interpreted as indicators of the biological,
evolutionary, ecological, or systematic importance of the characters
themselves.

"""

from pathlib import Path
import re
import random
import itertools
import numpy as np
import pandas as pd


TXT_PATH = Path(__file__).parent / "pdfToTxt_output.txt"
OUTPUT_XLSX = Path(__file__).parent / "检索表关键词统计.xlsx"

N_BOOTSTRAP = 1000
RANDOM_SEED = 42
ALPHA = 0.05


# ==========================
# 关键词
# ==========================

ORGAN_KEYWORDS = {
    "花": [
        "花", "花序", "花被", "花萼", "萼片", "花冠", "花瓣", "雄蕊", "雌蕊",
        "子房", "花柱", "柱头", "花盘", "苞片", "花梗", "雄花", "雌花"
    ],
    "果实": ["果", "果实", "蒴果", "瘦果", "浆果", "核果", "荚果", "角果"],
    "种子": ["种子", "胚珠", "种皮", "胚乳"],
    "根": ["根", "根状茎", "块根", "须根", "主根"],
    "茎": ["茎", "枝", "小枝", "节", "节间", "地下茎", "匍匐茎"],
    "叶": ["叶", "叶片", "叶柄", "托叶", "叶缘", "叶脉", "全缘", "锯齿", "裂片"],
}

FLOWER_FEATURE_GROUPS = {
    "花序": [
        "花序", "总状花序", "穗状花序", "圆锥花序", "头状花序",
        "伞形花序", "复伞形花序", "聚伞花序", "柔荑花序",
        "肉穗花序", "伞房花序", "隐头花序"
    ],
    "花被": [
        "花被", "花萼", "萼片", "副萼", "花冠", "花瓣", "花被片"
    ],
    "雄蕊": [
        "雄蕊", "花丝", "花药", "药室", "药隔", "退化雄蕊"
    ],
    "雌蕊": [
        "雌蕊", "子房", "花柱", "柱头", "胚珠"
    ],
    "花性": [
        "两性花", "单性花", "雄花", "雌花", "杂性花",
        "雌雄同株", "雌雄异株"
    ],
    "子房位置": [
        "子房上位", "子房半下位", "子房下位"
    ],
    "合生离生": [
        "合生", "离生", "联合", "分离", "连合"
    ],
    "对称性": [
        "辐射对称", "两侧对称"
    ],
    "苞片结构": [
        "苞片", "小苞片", "苞叶", "佛焰苞"
    ],
    "特殊结构": [
        "距", "唇瓣", "旗瓣", "翼瓣", "龙骨瓣", "副花冠", "蜜腺", "花盘"
    ],
}


# ==========================
# 条目分割
# ==========================

def clean_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"===== Page \d+ =====", "\n", text)
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    return text


def is_key_entry_start(line):
    return re.match(r"^([0-9]+|[lI])\s*[abAB]\s*[\.．、]", line) is not None


def normalize_entry_start(line):
    line = re.sub(r"^[lI]\s*([abAB])", r"1\1", line)
    return line


def split_entries(text):
    text = clean_text(text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    entries = []
    current = []

    for line in lines:
        line = normalize_entry_start(line)

        if is_key_entry_start(line):
            if current:
                entries.append(" ".join(current))
            current = [line]
        else:
            if current:
                current.append(line)

    if current:
        entries.append(" ".join(current))

    entries = [
        e for e in entries
        if len(e) >= 8 and re.match(r"^([0-9]+)\s*[abAB]\s*[\.．、]", e)
    ]

    return entries


# ==========================
# 统计函数
# ==========================

def contains_any(text, keywords):
    return int(any(k in text for k in keywords))


def bootstrap_category_stats(df, columns, n_bootstrap=1000, seed=42):
    """
    对每个类别做Bootstrap，返回比例均值和95%置信区间。
    """
    rng = np.random.default_rng(seed)
    n = len(df)

    rows = []
    boot_records = []

    for i in range(1, n_bootstrap + 1):
        sampled_index = rng.integers(0, n, size=n)
        sampled_df = df.iloc[sampled_index]

        record = {"bootstrap_id": i}

        for col in columns:
            record[col] = sampled_df[col].mean()

        boot_records.append(record)

    df_boot = pd.DataFrame(boot_records)

    for col in columns:
        values = df_boot[col]

        rows.append({
            "类别": col,
            "原始出现条目数": int(df[col].sum()),
            "总条目数": n,
            "原始比例": df[col].mean(),
            "Bootstrap均值": values.mean(),
            "95%CI下限": values.quantile(0.025),
            "95%CI上限": values.quantile(0.975),
        })

    return pd.DataFrame(rows), df_boot


def bootstrap_pairwise_diff(df_boot, columns):
    """
    两两比较Bootstrap比例差异。
    如果95%CI不跨0，则认为差异较明显。
    """
    rows = []

    for a, b in itertools.combinations(columns, 2):
        diff = df_boot[a] - df_boot[b]

        ci_low = diff.quantile(0.025)
        ci_high = diff.quantile(0.975)

        if ci_low > 0 or ci_high < 0:
            significant = "是"
        else:
            significant = "否"

        rows.append({
            "A": a,
            "B": b,
            "A-B原始比例差": None,
            "A-B Bootstrap均值差": diff.mean(),
            "95%CI下限": ci_low,
            "95%CI上限": ci_high,
            "95%CI是否不跨0": significant
        })

    return pd.DataFrame(rows)


# ==========================
# 主程序
# ==========================

def main():
    random.seed(RANDOM_SEED)

    text = TXT_PATH.read_text(encoding="utf-8")
    entries = split_entries(text)

    if not entries:
        raise ValueError("没有分割出检索条目。请检查OCR文本或分割正则。")

    df_entries = pd.DataFrame({
        "entry_id": range(1, len(entries) + 1),
        "content": entries
    })

    df_entry_stats = df_entries.copy()

    for organ, keywords in ORGAN_KEYWORDS.items():
        df_entry_stats[organ] = df_entry_stats["content"].apply(
            lambda x: contains_any(x, keywords)
        )

    for group, keywords in FLOWER_FEATURE_GROUPS.items():
        df_entry_stats[f"花特征_{group}"] = df_entry_stats["content"].apply(
            lambda x: contains_any(x, keywords)
        )

    # 器官统计
    organ_cols = list(ORGAN_KEYWORDS.keys())
    df_organ_ci, df_organ_boot = bootstrap_category_stats(
        df_entry_stats,
        organ_cols,
        n_bootstrap=N_BOOTSTRAP,
        seed=RANDOM_SEED
    )

    df_organ_diff = bootstrap_pairwise_diff(df_organ_boot, organ_cols)

    for i, row in df_organ_diff.iterrows():
        a = row["A"]
        b = row["B"]
        df_organ_diff.loc[i, "A-B原始比例差"] = (
            df_entry_stats[a].mean() - df_entry_stats[b].mean()
        )

    # 花特征统计
    flower_cols = [f"花特征_{group}" for group in FLOWER_FEATURE_GROUPS]

    df_flower_ci, df_flower_boot = bootstrap_category_stats(
        df_entry_stats,
        flower_cols,
        n_bootstrap=N_BOOTSTRAP,
        seed=RANDOM_SEED + 1
    )

    df_flower_ci["类别"] = df_flower_ci["类别"].str.replace("花特征_", "", regex=False)

    df_flower_diff = bootstrap_pairwise_diff(df_flower_boot, flower_cols)

    for i, row in df_flower_diff.iterrows():
        a = row["A"]
        b = row["B"]
        df_flower_diff.loc[i, "A-B原始比例差"] = (
            df_entry_stats[a].mean() - df_entry_stats[b].mean()
        )

    df_flower_diff["A"] = df_flower_diff["A"].str.replace("花特征_", "", regex=False)
    df_flower_diff["B"] = df_flower_diff["B"].str.replace("花特征_", "", regex=False)

    # 关键词说明
    df_organ_keywords = pd.DataFrame([
        {
            "类别": organ,
            "关键词数组": "；".join(keywords)
        }
        for organ, keywords in ORGAN_KEYWORDS.items()
    ])

    df_flower_keywords = pd.DataFrame([
        {
            "花部特征类别": group,
            "关键词数组": "；".join(keywords)
        }
        for group, keywords in FLOWER_FEATURE_GROUPS.items()
    ])

    df_params = pd.DataFrame({
        "参数": [
            "输入文件",
            "输出文件",
            "Bootstrap次数",
            "随机种子",
            "条目总数",
            "条目分割规则",
            "统计单位",
            "显著性判断"
        ],
        "值": [
            str(TXT_PATH),
            str(OUTPUT_XLSX),
            N_BOOTSTRAP,
            RANDOM_SEED,
            len(entries),
            "识别 1a./1b./2a./2b. 等检索表对比条目；兼容 la./lb. OCR错误",
            "检索表条目",
            "Bootstrap差值95%置信区间不跨0"
        ]
    })

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        df_entries.to_excel(writer, sheet_name="全部条目", index=False)
        df_entry_stats.to_excel(writer, sheet_name="全部条目统计", index=False)

        df_organ_ci.to_excel(writer, sheet_name="器官Bootstrap统计", index=False)
        df_organ_diff.to_excel(writer, sheet_name="器官两两比较", index=False)

        df_flower_ci.to_excel(writer, sheet_name="花特征Bootstrap统计", index=False)
        df_flower_diff.to_excel(writer, sheet_name="花特征两两比较", index=False)

        df_organ_boot.to_excel(writer, sheet_name="器官Bootstrap原始结果", index=False)
        df_flower_boot.to_excel(writer, sheet_name="花特征Bootstrap原始结果", index=False)

        df_organ_keywords.to_excel(writer, sheet_name="器官关键词", index=False)
        df_flower_keywords.to_excel(writer, sheet_name="花特征关键词", index=False)
        df_params.to_excel(writer, sheet_name="参数说明", index=False)

    print("完成")
    print(f"分割出条目数：{len(entries)}")
    print(f"输出文件：{OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
