import pandas as pd
import numpy as np
from pathlib import Path
import shutil
from PIL import Image
import matplotlib.pyplot as plt

def descargar_y_preparar_dataset():
    print("Descargando dataset")
    import subprocess
    subprocess.run([
        "kaggle", "datasets", "download", 
        "-d", "jessicali9530/celeba-dataset"
    ])
    
    print("Descomprimiendo")
    subprocess.run(["unzip", "-q", "celeba-dataset.zip", "-d", "celeba_data"])
    
    base_path = Path('celeba_data')
    img_path = base_path / 'img_align_celeba' / 'img_align_celeba'
    output_path = Path('dataset_seleccionado')
    output_path.mkdir(exist_ok=True)
    
    print("Leyendo metadata")
    identity_df = pd.read_csv(
        base_path / 'identity_CelebA.txt', 
        sep=' ', 
        header=None, 
        names=['image', 'identity']
    )
    
    attr_df = pd.read_csv(base_path / 'list_attr_celeba.csv')
    
    df = identity_df.merge(attr_df, left_on='image', right_on='image_id')
    
    print("Filtrando personas con múltiples imágenes")
    identity_counts = df['identity'].value_counts()
    valid_identities = identity_counts[identity_counts >= 4].index
    df_filtered = df[df['identity'].isin(valid_identities)]
    
    male_ids = df_filtered[df_filtered['Male'] == 1]['identity'].unique()
    female_ids = df_filtered[df_filtered['Male'] == -1]['identity'].unique()
    
    np.random.seed(42)
    selected_males = np.random.choice(male_ids, size=5, replace=False)
    selected_females = np.random.choice(female_ids, size=5, replace=False)
    
    selected_identities = list(selected_males) + list(selected_females)
    
    print("Copiando imágenes seleccionadas")
    total_images = 0
    
    for identity_id in selected_identities:
        person_images = df_filtered[df_filtered['identity'] == identity_id]['image'].tolist()[:5]
        person_gender = df_filtered[df_filtered['identity'] == identity_id]['Male'].iloc[0]
        gender_label = 'male' if person_gender == 1 else 'female'
        
        person_folder = output_path / f'person_{identity_id}_{gender_label}'
        person_folder.mkdir(exist_ok=True)
        
        for img_name in person_images:
            src = img_path / img_name
            dst = person_folder / img_name
            if src.exists():
                shutil.copy(src, dst)
                total_images += 1
    
    print(f"\nCompletado")
    print(f"   Personas seleccionadas: {len(selected_identities)}")
    print(f"   Total de imagenes: {total_images}")
    print(f"   Ubicación: {output_path.absolute()}")
    
    return output_path

def preview_dataset(dataset_path, n_preview=3):
    """Muestra preview de las imágenes"""
    person_folders = sorted(list(Path(dataset_path).glob('person_*')))[:n_preview]
    
    for person_folder in person_folders:
        images = list(person_folder.glob('*.jpg'))[:5]
        
        fig, axes = plt.subplots(1, len(images), figsize=(15, 3))
        fig.suptitle(person_folder.name, fontsize=14)
        
        for ax, img_path in zip(axes, images):
            img = Image.open(img_path)
            ax.imshow(img)
            ax.axis('off')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    dataset_path = descargar_y_preparar_dataset()
    
    print("\nMostrando preview")
    preview_dataset(dataset_path)
