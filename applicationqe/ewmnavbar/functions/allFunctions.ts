// helper/allFunctions
import { allPages } from "../pages/allPages";
import { BrowserActions } from "./fBrowser";
import { getImage } from "../helper/getImage";
import { ComparePageFunction } from "./fComparePages";
import { clickButton, clickLink, typeinField, textExists, elemHasAttribute, elemVisible, safeMessage } from "./fElementHelper";

type Logger = (msg: string) => Promise<void>;

export class allFunctions {
  readonly Browser: BrowserActions;
  readonly img: getImage;
  readonly Broser: BrowserActions;
  readonly ComparePages: ComparePageFunction;
  readonly clickButton = clickButton;
  readonly clickLink = clickLink;
  readonly typeinField = typeinField;
  readonly textExists = textExists;
  readonly elemHasAttribute = elemHasAttribute;
  readonly elemVisible = elemVisible;
  readonly safeMessage = safeMessage;

  constructor(pages: allPages, logger: Logger) {
    const page = pages.page;
    const testInfo = pages.testInfo;
    this.img = new getImage(page, testInfo);
    this.Browser = new BrowserActions(page, logger);
    this.ComparePages = new ComparePageFunction(page, logger, testInfo);
  }
}