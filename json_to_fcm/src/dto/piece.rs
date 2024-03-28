use fcmlib::Piece;
use serde::{Deserialize, Serialize};

use crate::{PathDto, PieceFlagsDto};

#[derive(Serialize, Deserialize)]
pub struct PieceDto {
    width: u32,
    height: u32,
    expansion_limit: u32,
    reduction_limit: u32,
    transform: Option<(f32, f32, f32, f32, f32, f32)>,
    flags: PieceFlagsDto,
    label: String,
    paths: Vec<PathDto>,
}

impl From<&Piece> for PieceDto {
    fn from(piece: &Piece) -> PieceDto {
        PieceDto {
            width: piece.width,
            height: piece.height,
            expansion_limit: piece.expansion_limit_value,
            reduction_limit: piece.reduction_limit_value,
            transform: piece.transform,
            flags: PieceFlagsDto::from(&piece.restriction_flags),
            label: piece.label.clone(),
            paths: piece.paths.iter()
                .filter_map(|path| PathDto::try_from(path).ok())
                .collect(),
        }
    }
}

impl Into<Piece> for &PieceDto {
    fn into(self) -> Piece {
        Piece {
            width: self.width,
            height: self.height,
            transform: self.transform,
            expansion_limit_value: self.expansion_limit,
            reduction_limit_value: self.reduction_limit,
            restriction_flags: (&self.flags).into(),
            label: self.label.clone(),
            paths: self.paths.iter().map(|path| path.into()).collect(),
        }
    }
}

impl Into<Piece> for PieceDto {
    fn into(self) -> Piece {
        Into::into(&self)
    }
}
