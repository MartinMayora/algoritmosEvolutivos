# generar_conjuntos_candidatos.py - VERSIÓN FINAL CORREGIDA
import pandas as pd
import numpy as np
from pathlib import Path
import shutil

def generar_conjuntos_candidatos():
    """
    Genera múltiples conjuntos de candidatos para selección manual
    """
    
    print("="*60)
    print("Generación de Conjuntos Candidatos")
    print("="*60 + "\n")
    
    # PATHS CORREGIDOS - carpeta anidada!
    base_path = Path('../data')
    celeba_path = base_path / 'celeba_data'
    img_path = celeba_path / 'img_align_celeba' / 'img_align_celeba'  # ← DOBLE carpeta
    
    print(f"📁 Verificando rutas...")
    print(f"   Imágenes: {img_path.absolute()}")
    print(f"   Existe: {img_path.exists()}")
    
    if not img_path.exists():
        print(f"❌ No se encontró: {img_path}")
        return None
    
    # Contar imágenes
    n_images = len(list(img_path.glob('*.jpg')))
    print(f"   ✓ {n_images:,} imágenes encontradas\n")
    
    # Archivos
    identity_file = base_path / 'identity_CelebA.txt'
    attr_file = celeba_path / 'list_attr_celeba.csv'
    
    if not identity_file.exists():
        print(f"❌ No se encontró: {identity_file}")
        return None
    
    if not attr_file.exists():
        print(f"❌ No se encontró: {attr_file}")
        return None
    
    print(f"📊 Leyendo datos...")
    identity_df = pd.read_csv(identity_file, sep=' ', header=None, names=['image', 'identity'])
    attr_df = pd.read_csv(attr_file)
    
    print(f"   ✓ {len(identity_df):,} registros de identidad")
    print(f"   ✓ {len(attr_df):,} registros de atributos")
    
    # Merge
    df = identity_df.merge(attr_df, left_on='image', right_on='image_id', how='inner')
    print(f"   ✓ {len(df):,} registros después del merge")
    
    # Filtrar personas con 4-8 imágenes
    print(f"\n🔍 Filtrando personas...")
    identity_counts = df['identity'].value_counts()
    valid_identities = identity_counts[(identity_counts >= 4) & (identity_counts <= 8)].index
    df_filtered = df[df['identity'].isin(valid_identities)]
    
    print(f"   ✓ {len(valid_identities):,} personas con 4-8 imágenes")
    
    # Filtrar por calidad
    print(f"\n✨ Aplicando filtros de calidad...")
    quality_filter = (
        (df_filtered['Eyeglasses'] == -1) &
        (df_filtered['Wearing_Hat'] == -1) &
        (df_filtered['Blurry'] == -1)
    )
    
    df_quality = df_filtered[quality_filter]
    
    quality_identity_counts = df_quality['identity'].value_counts()
    final_valid_identities = quality_identity_counts[quality_identity_counts >= 4].index
    df_final = df_quality[df_quality['identity'].isin(final_valid_identities)]
    
    print(f"   ✓ {len(final_valid_identities):,} personas después de filtros")
    
    # Separar por género
    male_ids = df_final[df_final['Male'] == 1]['identity'].unique()
    female_ids = df_final[df_final['Male'] == -1]['identity'].unique()
    
    print(f"   ✓ Hombres: {len(male_ids):,}, Mujeres: {len(female_ids):,}")
    
    # Generar 5 conjuntos
    n_conjuntos = 5
    output_base = Path('../data/conjuntos_candidatos')
    output_base.mkdir(exist_ok=True)
    
    print(f"\n📁 Generando {n_conjuntos} conjuntos candidatos...\n")
    
    conjuntos_info = []
    
    for conjunto_idx in range(n_conjuntos):
        seed = 42 + conjunto_idx * 10
        np.random.seed(seed)
        
        n_males = min(3, len(male_ids))
        n_females = min(3, len(female_ids))
        
        selected_males = np.random.choice(male_ids, size=n_males, replace=False)
        selected_females = np.random.choice(female_ids, size=n_females, replace=False)
        selected_identities = list(selected_males) + list(selected_females)
        
        conjunto_folder = output_base / f'conjunto_{conjunto_idx + 1}'
        conjunto_folder.mkdir(exist_ok=True)
        
        conjunto_stats = {
            'conjunto': conjunto_idx + 1,
            'personas': []
        }
        
        total_images = 0
        
        for identity_id in selected_identities:
            person_data = df_final[df_final['identity'] == identity_id]
            person_images = person_data['image'].tolist()
            person_gender = person_data['Male'].iloc[0]
            gender_label = 'male' if person_gender == 1 else 'female'
            
            person_folder = conjunto_folder / f'person_{identity_id:04d}_{gender_label}'
            person_folder.mkdir(exist_ok=True)
            
            copied = 0
            for img_name in person_images:
                src = img_path / img_name
                dst = person_folder / img_name
                
                if src.exists():
                    shutil.copy(src, dst)
                    copied += 1
            
            total_images += copied
            
            conjunto_stats['personas'].append({
                'id': identity_id,
                'gender': gender_label,
                'n_images': copied,
                'folder': person_folder.name
            })
        
        conjunto_stats['total_images'] = total_images
        conjuntos_info.append(conjunto_stats)
        
        print(f"✓ Conjunto {conjunto_idx + 1}: {len(selected_identities)} personas, {total_images} imágenes")
    
    crear_resumen_html(output_base, conjuntos_info)
    
    print(f"\n✅ Conjuntos generados en: {output_base.absolute()}")
    print(f"\n👁️  Para ver las imágenes:")
    print(f"    xdg-open {output_base.absolute() / 'resumen.html'}")
    
    return output_base

def crear_resumen_html(output_path, conjuntos_info):
    """Crea un HTML para visualizar todos los conjuntos"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Conjuntos Candidatos - CelebA</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        .conjunto { background: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .conjunto h2 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .persona { margin: 20px 0; padding: 15px; background: #fafafa; border-left: 4px solid #2196F3; }
        .persona.male { border-left-color: #2196F3; }
        .persona.female { border-left-color: #E91E63; }
        .images { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
        .images img { width: 150px; height: 150px; object-fit: cover; border: 2px solid #ddd; border-radius: 5px; transition: transform 0.2s; cursor: pointer; }
        .images img:hover { transform: scale(2); z-index: 1000; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .stats { display: inline-block; background: #e3f2fd; padding: 5px 15px; border-radius: 20px; margin: 5px; font-size: 14px; }
        .gender-male { color: #1976D2; font-weight: bold; }
        .gender-female { color: #C2185B; font-weight: bold; }
        .instrucciones { margin-top: 40px; padding: 20px; background: #fff3cd; border-radius: 10px; border-left: 5px solid #ffc107; }
    </style>
</head>
<body>
    <h1>🎭 Conjuntos Candidatos para Selección Manual</h1>
    <p style="text-align: center;">Hacé hover sobre las imágenes para verlas más grandes. Elegí el conjunto con mejor calidad y variedad.</p>
"""
    
    for conjunto in conjuntos_info:
        html += f"""
    <div class="conjunto">
        <h2>Conjunto {conjunto['conjunto']}</h2>
        <div>
            <span class="stats">Total: {conjunto['total_images']} imágenes</span>
            <span class="stats">{len([p for p in conjunto['personas'] if p['gender'] == 'male'])} hombres</span>
            <span class="stats">{len([p for p in conjunto['personas'] if p['gender'] == 'female'])} mujeres</span>
        </div>
"""
        
        for persona in conjunto['personas']:
            gender_class = persona['gender']
            gender_label = '👨 Hombre' if persona['gender'] == 'male' else '👩 Mujer'
            
            html += f"""
        <div class="persona {gender_class}">
            <h3><span class="gender-{gender_class}">{gender_label}</span> - ID: {persona['id']} - {persona['n_images']} imágenes</h3>
            <div class="images">
"""
            
            person_folder = output_path / f"conjunto_{conjunto['conjunto']}" / persona['folder']
            images = sorted(list(person_folder.glob('*.jpg')))
            
            for img in images:
                rel_path = img.relative_to(output_path)
                html += f'<img src="{rel_path}" alt="{img.name}" title="{img.name}">'
            
            html += """
            </div>
        </div>
"""
        
        html += "</div>"
    
    html += """
    <div class="instrucciones">
        <h3>📝 Cómo Seleccionar:</h3>
        <ol>
            <li><strong>Verificá identidad:</strong> Todas las imágenes de cada persona deben ser claramente de la misma persona</li>
            <li><strong>Buscá variedad:</strong> Diferentes poses, expresiones, iluminación</li>
            <li><strong>Elegí tu conjunto favorito</strong></li>
        </ol>
        <p><strong>Una vez que elijas:</strong></p>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
# Copiar conjunto completo (ejemplo: conjunto_2)
cp -r ../data/conjuntos_candidatos/conjunto_2 ../data/dataset_final

# O copiar personas individuales
mkdir ../data/dataset_final
cp -r ../data/conjuntos_candidatos/conjunto_1/person_XXXX_male ../data/dataset_final/
        </pre>
    </div>
</body>
</html>
"""
    
    html_file = output_path / 'resumen.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)

def generar_conjunto_extra_grande():
    """Genera conjunto grande con 15 hombres + 15 mujeres"""
    
    print("\n" + "="*60)
    print("Generando Conjunto EXTRA")
    print("="*60 + "\n")
    
    base_path = Path('../data')
    celeba_path = base_path / 'celeba_data'
    img_path = celeba_path / 'img_align_celeba' / 'img_align_celeba'  # ← DOBLE carpeta
    
    identity_file = base_path / 'identity_CelebA.txt'
    attr_file = celeba_path / 'list_attr_celeba.csv'
    
    identity_df = pd.read_csv(identity_file, sep=' ', header=None, names=['image', 'identity'])
    attr_df = pd.read_csv(attr_file)
    df = identity_df.merge(attr_df, left_on='image', right_on='image_id', how='inner')
    
    identity_counts = df['identity'].value_counts()
    valid_identities = identity_counts[(identity_counts >= 4) & (identity_counts <= 8)].index
    df_filtered = df[df['identity'].isin(valid_identities)]
    
    quality_filter = (
        (df_filtered['Eyeglasses'] == -1) &
        (df_filtered['Wearing_Hat'] == -1) &
        (df_filtered['Blurry'] == -1)
    )
    
    df_quality = df_filtered[quality_filter]
    quality_identity_counts = df_quality['identity'].value_counts()
    final_valid_identities = quality_identity_counts[quality_identity_counts >= 4].index
    df_final = df_quality[df_quality['identity'].isin(final_valid_identities)]
    
    male_ids = df_final[df_final['Male'] == 1]['identity'].unique()
    female_ids = df_final[df_final['Male'] == -1]['identity'].unique()
    
    np.random.seed(99)
    n_per_gender = 15
    
    selected_males = np.random.choice(male_ids, size=min(n_per_gender, len(male_ids)), replace=False)
    selected_females = np.random.choice(female_ids, size=min(n_per_gender, len(female_ids)), replace=False)
    selected_identities = list(selected_males) + list(selected_females)
    
    output_path = Path('../data/conjunto_extra_grande')
    output_path.mkdir(exist_ok=True)
    
    print(f"Copiando {len(selected_identities)} personas...")
    
    total_copied = 0
    for identity_id in selected_identities:
        person_data = df_final[df_final['identity'] == identity_id]
        person_images = person_data['image'].tolist()
        person_gender = person_data['Male'].iloc[0]
        gender_label = 'male' if person_gender == 1 else 'female'
        
        person_folder = output_path / f'person_{identity_id:04d}_{gender_label}'
        person_folder.mkdir(exist_ok=True)
        
        for img_name in person_images:
            src = img_path / img_name
            dst = person_folder / img_name
            if src.exists():
                shutil.copy(src, dst)
                total_copied += 1
    
    print(f"\n✅ Conjunto EXTRA generado: {output_path.absolute()}")
    print(f"   {len(selected_identities)} personas, {total_copied} imágenes totales")

if __name__ == "__main__":
    output = generar_conjuntos_candidatos()
    generar_conjunto_extra_grande()
    
    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)
    print("\n📂 Tienes:")
    print("   1. ../data/conjuntos_candidatos/ - 5 conjuntos pequeños")
    print("   2. ../data/conjunto_extra_grande/ - 30 personas")
    print("\n👁️  Abrí el HTML:")
    print("   xdg-open ../data/conjuntos_candidatos/resumen.html")