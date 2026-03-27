import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# HISTOGRAM
# -----------------------------

def histogram(df, col, bins=20):

    fig, ax = plt.subplots()

    ax.hist(df[col].dropna(), bins=bins)

    ax.set_title(f"Histogram of {col}")

    return fig


# -----------------------------
# BOXPLOT
# -----------------------------

def boxplot(df, col):

    fig, ax = plt.subplots()

    ax.boxplot(df[col].dropna())

    ax.set_title(f"Boxplot of {col}")

    return fig


# -----------------------------
# SCATTER
# -----------------------------

def scatter(df, x, y):

    fig, ax = plt.subplots()

    ax.scatter(df[x], df[y])

    ax.set_xlabel(x)
    ax.set_ylabel(y)

    return fig


# -----------------------------
# LINE
# -----------------------------

def line(df, x, y):

    fig, ax = plt.subplots()

    ax.plot(df[x], df[y])

    ax.set_xlabel(x)
    ax.set_ylabel(y)

    return fig


# -----------------------------
# BAR
# -----------------------------

def bar(df, category, value, agg, top_n):

    grouped = df.groupby(category)[value].agg(agg)

    grouped = grouped.sort_values(ascending=False).head(top_n)

    fig, ax = plt.subplots()

    grouped.plot(kind="bar", ax=ax)

    ax.set_title(f"{agg} of {value} by {category}")

    return fig


# -----------------------------
# HEATMAP
# -----------------------------

def heatmap(df):

    corr = df.select_dtypes(include="number").corr()

    fig, ax = plt.subplots()

    cax = ax.matshow(corr)

    fig.colorbar(cax)

    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))

    ax.set_xticklabels(corr.columns, rotation=90)
    ax.set_yticklabels(corr.columns)

    return fig