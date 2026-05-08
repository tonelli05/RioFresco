import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def gerar_fluxograma():
    # Garantir que a pasta assets existe
    os.makedirs('assets', exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 8))

    # Passos do projeto definidos na requisição
    steps = [
        "1. Baixar os Dados\n(CSVs, etc.)",
        "2. Processar Datasets\n(EDA e Processar Verde)",
        "3. Integração\n(Cruzamento dos Datasets)",
        "4. Machine Learning\n(Regressão e Clusterização)"
    ]

    box_width = 4
    box_height = 1
    spacing = 1.8

    x = 2
    y_start = 8

    for i, step in enumerate(steps):
        y = y_start - i * spacing
        
        # Criar caixa com cantos arredondados
        rect = patches.FancyBboxPatch(
            (x, y), box_width, box_height,
            boxstyle="round,pad=0.2",
            linewidth=2, edgecolor='#1f77b4', facecolor='#e6f2ff'
        )
        ax.add_patch(rect)
        
        # Adicionar texto
        ax.text(
            x + box_width/2, y + box_height/2,
            step,
            ha='center', va='center', fontsize=12, fontweight='bold',
            color='#333333'
        )
        
        # Adicionar setas entre as caixas
        if i < len(steps) - 1:
            next_y = y_start - (i + 1) * spacing
            
            # Start of arrow is bottom of current box (x + width/2, y)
            # End of arrow is top of next box (x + width/2, next_y + height)
            ax.annotate(
                '',
                xy=(x + box_width/2, next_y + box_height + 0.1), 
                xytext=(x + box_width/2, y - 0.1),
                arrowprops=dict(arrowstyle="->", lw=2, color='#1f77b4')
            )

    # Ajustes finais da plotagem
    ax.set_xlim(0, 8)
    ax.set_ylim(2, 10)
    ax.axis('off')
    plt.title("Fluxo do Projeto", fontsize=16, fontweight='bold', pad=20)

    # Salvar a imagem
    caminho = os.path.join("assets", "fluxo_projeto.png")
    plt.tight_layout()
    plt.savefig(caminho, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    gerar_fluxograma()
