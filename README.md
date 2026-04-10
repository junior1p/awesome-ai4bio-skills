# 🧬 awesome-ai4bio-skills

> **47 curated computational biology & bioinformatics skills for AI agents.**
> 精选的计算生物学与生物信息学 AI Agent Skills，独立部署于 GitHub Pages。

本仓库从 [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) 中提取计算生物学相关部分，重组成独立站点，方便单独部署和引用。

---

## 📂 Skills (47)

### 🔬 Sequence & Genomics
pysam · biopython · scikit-bio · gget · gtars · bioservices · deeptools · polars-bio · dask · zarr-python · tiledbvcf · polars

### 🧫 Single-Cell & Multi-Omics
scanpy · scvi-tools · anndata · scvelo · cellxgene-census · arboreto · lamindb · geniml · pydeseq2 · hypogenic · primekg

### 💊 Protein & Structure
esm · rdkit · deepchem · torchdrug · diffdock · datamol · molfeat · medchem · pytdc · pymatgen · cobrapy · molecular-dynamics · glycoengineering · adaptyv · etetoolkit

### ⚗️ Mass Spectrometry & Metabolism
matchms · pyopenms

### 📚 Literature & Databases
database-lookup · paper-lookup

### 📊 Visualization & Analysis
scientific-visualization · exploratory-data-analysis · networkx · matplotlib · seaborn

---

## 🌐 Live Site

**https://junior1p.github.io/awesome-ai4bio-skills/**

每个 Skill 拥有独立页面，包含：
- ✅ 完整使用文档（SKILL.md 渲染）
- ✅ Reference 子文档（references/ 目录）
- ✅ 代码示例与最佳实践
- ✅ 左侧导航栏，可跳转任意 Skill

---

## 🏗️ 本地构建

```bash
# 安装依赖（仅需 Python 标准库）
pip install markdown  # 可选，增强渲染效果

# 生成静态站点
python generate_site.py

# 站点输出到 site/ 目录
cd site && python -m http.server 8080
```

---

## 📦 部署到 GitHub Pages

站点直接 Push 到 `main` 分支，启用 GitHub Pages 后即可访问：

```bash
git add .
git commit -m "Initial: 47 computational biology skills"
git branch -M main
git push -u origin main
```

然后在 GitHub 仓库 Settings → Pages → Source: `main` branch `/ (root)`。

---

## 🔄 与 scientific-agent-skills 保持同步

```bash
# 从上游同步更新
cd ~/scientific-agent-skills
git pull origin main

# 重新运行生成器
python ~/awesome-ai4bio-skills/generate_site.py
```

---

## ⚠️ Disclaimer

本仓库 Skill 版权属于 [K-Dense Inc.](https://github.com/K-Dense-AI/scientific-agent-skills)，遵循各 Skill 原有 License。仅提取整理，不修改原始内容。
