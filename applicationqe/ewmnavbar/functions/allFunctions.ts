// helper/allFunctions
import { allPages } from "../pages/allPages";
import { BrowserActions } from "./fBrowser";
import { ElementHelper } from "./fElement";
import { getImage } from "../helper/getImage";
import { ComparePageFunction } from "./fComparePages";

type Logger = (msg: string) => Promise<void>;

export class allFunctions {
  readonly Browser: BrowserActions;
  readonly img: getImage;
  readonly Element: ElementHelper;
  readonly ComparePages: ComparePageFunction;
  

  constructor(pages: allPages, logger: Logger) {
    const page = pages.page;
    const testInfo = pages.testInfo;
    this.img = new getImage(page, testInfo);
    this.Browser = new BrowserActions(page, logger);
    this.Element = new ElementHelper(logger);
    this.ComparePages = new ComparePageFunction(page, logger, testInfo);
  }
}