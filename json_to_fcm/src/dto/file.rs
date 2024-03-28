use fcmlib::{FcmFile, FileHeader, FileVariant, Generator, PieceTable};
use serde::{Deserialize, Serialize};

use crate::CutDataDto;
use crate::dto::serde_base64;
use crate::PieceDto;

#[derive(Serialize, Deserialize)]
pub struct FileDto {
    content_id: u32,
    short_name: String,
    long_name: String,
    author_name: String,
    copyright: String,
    cut_data: CutDataDto,
    thumbnail: ThumbnailDto,
    pieces: Vec<PieceDto>,
}

#[derive(Serialize, Deserialize)]
pub struct ThumbnailDto {
    block_width: u8,
    block_height: u8,
    #[serde(with = "serde_base64")]
    data: Vec<u8>,
}

impl From<&FcmFile> for FileDto {
    fn from(file: &FcmFile) -> FileDto {
        FileDto {
            content_id: file.file_header.content_id.clone(),
            short_name: file.file_header.short_name.clone(),
            long_name: file.file_header.long_name.clone(),
            author_name: file.file_header.author_name.clone(),
            copyright: file.file_header.copyright.clone(),
            cut_data: CutDataDto::from(&file.cut_data),
            thumbnail: ThumbnailDto {
                block_width: file.file_header.thumbnail_block_size_width,
                block_height: file.file_header.thumbnail_block_size_height,
                data: file.file_header.thumbnail.clone(),
            },
            pieces: file.piece_table.pieces.iter()
                .map(|(_, piece)| PieceDto::from(piece))
                .collect(),
        }
    }
}

impl Into<FcmFile> for &FileDto {
    fn into(self) -> FcmFile {
        FcmFile {
            file_header: FileHeader {
                variant: FileVariant::FCM,
                version: "0100".to_string(),
                content_id: self.content_id,
                short_name: self.short_name.clone(),
                long_name: self.long_name.clone(),
                author_name: self.author_name.clone(),
                copyright: self.copyright.clone(),
                thumbnail_block_size_width: self.thumbnail.block_width,
                thumbnail_block_size_height: self.thumbnail.block_height,
                thumbnail: self.thumbnail.data.clone(),
                generator: Generator::App(0),
                print_to_cut: None,
            },
            cut_data: (&self.cut_data).into(),
            piece_table: PieceTable {
                pieces: self.pieces.iter()
                    .enumerate()
                    .map(|(index, piece)| (index as u16, piece.into()))
                    .collect()
            },
        }
    }
}

impl Into<FcmFile> for FileDto {
    fn into(self) -> FcmFile {
        Into::into(&self)
    }
}
