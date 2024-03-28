use fcmlib::PathTool;
use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct PathFlagsDto {
    open: bool,
    fill: bool,
    seam_allowance: bool,
    auto_align: bool,
    tool_cut: bool,
    tool_draw: bool,
    tool_draw_only: bool,
    tool_rhinestone: bool,
    tool_emboss: bool,
    tool_foil: bool,
    tool_perforating: bool,
}

impl From<&PathTool> for PathFlagsDto {
    fn from(tool: &PathTool) -> PathFlagsDto {
        PathFlagsDto {
            open: tool.contains(PathTool::PATH_OPEN),
            fill: tool.contains(PathTool::FILL),
            seam_allowance: tool.contains(PathTool::SEAM_ALLOWANCE),
            auto_align: tool.contains(PathTool::AUTO_ALIGN),
            tool_cut: tool.contains(PathTool::TOOL_CUT),
            tool_draw: tool.contains(PathTool::TOOL_DRAW),
            tool_draw_only: tool.contains(PathTool::TOOL_DRAW_ONLY),
            tool_rhinestone: tool.contains(PathTool::TOOL_RHINESTONE),
            tool_emboss: tool.contains(PathTool::TOOL_EMBOSS),
            tool_foil: tool.contains(PathTool::TOOL_FOIL),
            tool_perforating: tool.contains(PathTool::TOOL_PERFORATING),
        }
    }
}

impl Into<PathTool> for &PathFlagsDto {
    fn into(self) -> PathTool {
        PathTool::from_iter(PathTool::all().iter().filter(|value| match value {
            &PathTool::PATH_OPEN => self.open,
            &PathTool::FILL => self.fill,
            &PathTool::SEAM_ALLOWANCE => self.seam_allowance,
            &PathTool::AUTO_ALIGN => self.auto_align,
            &PathTool::TOOL_CUT => self.tool_cut,
            &PathTool::TOOL_DRAW => self.tool_draw,
            &PathTool::TOOL_DRAW_ONLY => self.tool_draw_only,
            &PathTool::TOOL_RHINESTONE => self.tool_rhinestone,
            &PathTool::TOOL_EMBOSS => self.tool_emboss,
            &PathTool::TOOL_FOIL => self.tool_foil,
            &PathTool::TOOL_PERFORATING => self.tool_perforating,
            _ => false,
        }))
    }
}

impl Into<PathTool> for PathFlagsDto {
    fn into(self) -> PathTool {
        Into::into(&self)
    }
}
