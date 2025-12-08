def visualize_results(pareto_front, logbook, output_dir='../../results/plots'):
    import matplotlib.pyplot as plt
    from pathlib import Path
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Extract fitness values
    fits = np.array([ind.fitness.values for ind in pareto_front])
    
    ax.scatter(fits[:, 0], fits[:, 1], s=100, alpha=0.7, edgecolors='black')
    ax.set_xlabel('Identity Similarity (f1)', fontsize=12)
    ax.set_ylabel('Gender Probability (f2)', fontsize=12)
    ax.set_title('Pareto Front - Gender Transformation', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'pareto_front.png', dpi=300)
    plt.close()

    gen = logbook.select("gen")
    avg_f1 = [avg[0] for avg in logbook.select("avg")]
    avg_f2 = [avg[1] for avg in logbook.select("avg")]
    max_f1 = [mx[0] for mx in logbook.select("max")]
    max_f2 = [mx[1] for mx in logbook.select("max")]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    ax1.plot(gen, avg_f1, label='Average', linewidth=2)
    ax1.plot(gen, max_f1, label='Maximum', linewidth=2, linestyle='--')
    ax1.set_xlabel('Generation', fontsize=12)
    ax1.set_ylabel('Identity Similarity (f1)', fontsize=12)
    ax1.set_title('Evolution of Identity Preservation', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(gen, avg_f2, label='Average', linewidth=2)
    ax2.plot(gen, max_f2, label='Maximum', linewidth=2, linestyle='--')
    ax2.set_xlabel('Generation', fontsize=12)
    ax2.set_ylabel('Gender Probability (f2)', fontsize=12)
    ax2.set_title('Evolution of Gender Transformation', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'evolution_progress.png', dpi=300)
    plt.close()
    
    print(f"Saved visualizations to {output_dir}")

def save_generated_images(pareto_front, stylegan, output_dir='../../results/images'):
    from pathlib import Path
    from PIL import Image
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, ind in enumerate(pareto_front):
        w = np.array(ind)
        img = stylegan.generate(w)
        
]        img_pil = Image.fromarray(img)
        filename = f'pareto_{i:03d}_f1={ind.fitness.values[0]:.3f}_f2={ind.fitness.values[1]:.3f}.png'
        img_pil.save(output_dir / filename)
    
    print(f"Saved {len(pareto_front)} generated images to {output_dir}")