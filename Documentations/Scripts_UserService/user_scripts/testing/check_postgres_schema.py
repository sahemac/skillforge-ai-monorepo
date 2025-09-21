#!/usr/bin/env python3
"""
Vérifier le schéma PostgreSQL
"""

import psycopg2

def check_users_table():
    """Vérifier la structure de la table users."""
    
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='skillforge_db',
        user='skillforge_user',
        password='Psaumes@27'
    )
    
    cursor = conn.cursor()
    
    # Vérifier les colonnes de la table users
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        ORDER BY ordinal_position;
    """)
    
    print("=== Colonnes de la table 'users' ===")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
    
    print(f"\nTotal colonnes: {len(columns)}")
    
    # Vérifier si full_name existe
    full_name_exists = any(col[0] == 'full_name' for col in columns)
    print(f"Colonne 'full_name' existe: {'OUI' if full_name_exists else 'NON'}")
    
    cursor.close()
    conn.close()
    
    return full_name_exists

if __name__ == "__main__":
    check_users_table()