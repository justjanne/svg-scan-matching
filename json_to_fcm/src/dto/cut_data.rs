use fcmlib::{CutData, FileType};
use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct CutDataDto {
    mat_id: u32,
    cut_width: u32,
    cut_height: u32,
    seam_allowance_width: u32,
}

impl From<&CutData> for CutDataDto {
    fn from(cut_data: &CutData) -> CutDataDto {
        CutDataDto {
            mat_id: cut_data.mat_id,
            cut_width: cut_data.cut_width,
            cut_height: cut_data.cut_height,
            seam_allowance_width: cut_data.seam_allowance_width,
        }
    }
}

impl Into<CutData> for &CutDataDto {
    fn into(self) -> CutData {
        CutData {
            file_type: FileType::Cut,
            mat_id: self.mat_id,
            cut_width: self.cut_width,
            cut_height: self.cut_height,
            seam_allowance_width: self.seam_allowance_width,
            alignment: None,
        }
    }
}

impl Into<CutData> for CutDataDto {
    fn into(self) -> CutData {
        Into::into(&self)
    }
}
