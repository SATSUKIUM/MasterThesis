#pragma once
#include <TCanvas.h>
#include <TSystem.h>
#include <TString.h>
#include <stdexcept>
// Keep the vector drawing; normalize page origin/rotation and symmetric margins.
inline void save_figure_pdf(TCanvas& canvas, const char* filename) {
  canvas.SaveAs(filename);
  const auto command = TString::Format(
    "pdfcrop --hires --margins 2 \"%s\" \"%s\" > /dev/null", filename, filename);
  if (gSystem->Exec(command.Data()) != 0)
    throw std::runtime_error("pdfcrop failed: figure page was not normalized");
}
