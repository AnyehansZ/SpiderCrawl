import zipfile
from pathlib import Path
from datetime import datetime
from app.database.db import get_connection
from app.config import EPUB_OUTPUT_DIR

class EPUBBuilder:
    def __init__(self, novel_id: int):
        self.novel_id = novel_id
        self.novel = self.get_novel_data()
        self.chapters = self.get_chapters()
    
    def get_novel_data(self) -> dict:
        """Fetch novel metadata from DB"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT n.*, m.cover_url, m.description 
            FROM novels n
            LEFT JOIN metadata m ON n.id = m.novel_id
            WHERE n.id = ?
        ''', (self.novel_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_chapters(self) -> list:
        """Fetch all chapters ordered by chapter_num"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM chapters 
            WHERE novel_id = ? 
            ORDER BY chapter_num ASC
        ''', (self.novel_id,))
        chapters = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return chapters
    
    def generate_chapter_xhtml(self, chapter: dict) -> str:
        """Generate XHTML for single chapter"""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{chapter['title']}</title>
    <meta charset="utf-8"/>
</head>
<body>
    <h1>{chapter['title']}</h1>
    <div class="chapter-content">
        {chapter['content'].replace('\n', '<br/>')}
    </div>
</body>
</html>'''
    
    def generate_opf(self) -> str:
        """Generate content.opf (metadata + manifest)"""
        manifest_items = '\n'.join([
            f'        <item id="ch{i:03d}" href="chapters/ch_{i:03d}.xhtml" media-type="application/xhtml+xml"/>'
            for i in range(1, len(self.chapters) + 1)
        ])
        
        spine_items = '\n'.join([
            f'        <itemref idref="ch{i:03d}"/>'
            for i in range(1, len(self.chapters) + 1)
        ])
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uuid">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{self.novel['title']}</dc:title>
        <dc:creator>{self.novel['author']}</dc:creator>
        <dc:description>{self.novel.get('description', '')}</dc:description>
        <dc:date>{datetime.now().isoformat()}</dc:date>
        <dc:identifier id="uuid">urn:uuid:{self.novel_id}</dc:identifier>
    </metadata>
    <manifest>
        <item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
{manifest_items}
    </manifest>
    <spine toc="toc">
{spine_items}
    </spine>
</package>'''
    
    def generate_ncx(self) -> str:
        """Generate table of contents (toc.ncx)"""
        nav_points = '\n'.join([
            f'''        <navPoint id="ch{i:03d}" playOrder="{i}">
            <navLabel><text>{ch['title']}</text></navLabel>
            <content src="chapters/ch_{i:03d}.xhtml"/>
        </navPoint>'''
            for i, ch in enumerate(self.chapters, 1)
        ])
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{self.novel_id}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{self.novel['title']}</text>
    </docTitle>
    <navMap>
{nav_points}
    </navMap>
</ncx>'''
    
    def build(self, output_name: str = None) -> str:
        """Build EPUB file"""
        if not self.novel:
            raise ValueError(f"Novel {self.novel_id} not found")
        
        output_name = output_name or f"{self.novel['title'].replace(' ', '_')}.epub"
        output_path = EPUB_OUTPUT_DIR / output_name
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub:
            # mimetype (uncompressed, first)
            epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
            
            # container.xml
            container = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
            epub.writestr('META-INF/container.xml', container)
            
            # OPF and NCX
            epub.writestr('OEBPS/content.opf', self.generate_opf())
            epub.writestr('OEBPS/toc.ncx', self.generate_ncx())
            
            # Chapters
            for i, chapter in enumerate(self.chapters, 1):
                xhtml = self.generate_chapter_xhtml(chapter)
                epub.writestr(f'OEBPS/chapters/ch_{i:03d}.xhtml', xhtml)
        
        print(f"✓ EPUB created: {output_path}")
        return str(output_path)